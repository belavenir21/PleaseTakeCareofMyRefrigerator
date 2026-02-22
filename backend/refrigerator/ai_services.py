"""
AI 서비스 모듈 - V2
영수증 분석, 사진 식재료 인식 등 AI 관련 기능
Groq 공식 라이브러리 사용
"""
import base64
import json
import re
from io import BytesIO
from datetime import date, timedelta

from django.conf import settings
from PIL import Image as PILImage

from master.models import IngredientMaster, find_master_by_name
from config.constants import CATEGORY_DEFAULTS


def get_groq_client():
    """Groq 클라이언트 반환"""
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        return None
    
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None


def get_api_config():
    """현재 사용할 API 설정 반환"""
    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    gemini_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
    
    if groq_key:
        return {
            'type': 'groq',
            'key': groq_key,
            'model': 'llama-3.3-70b-versatile',
            'vision_model': 'llama-3.2-11b-vision-preview'
        }
    elif gemini_key:
        return {
            'type': 'gemini',
            'key': gemini_key,
            'url': f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
        }
    else:
        return None


def call_groq_text(prompt: str) -> str:
    """Groq 텍스트 API 호출 (공식 라이브러리)"""
    client = get_groq_client()
    if not client:
        raise ValueError("Groq API 키가 설정되지 않았습니다.")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=4096
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            raise Exception("AI 서비스 사용량 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
        raise Exception(f"AI API 오류: {error_msg[:150]}")


def call_groq_vision(prompt: str, image_base64: str) -> str:
    """Groq Vision API 호출 (공식 라이브러리)"""
    client = get_groq_client()
    if not client:
        raise ValueError("Groq API 키가 설정되지 않았습니다.")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }],
            model="llama-3.2-11b-vision-preview",
            temperature=0.3,
            max_tokens=4096
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            raise Exception("AI 서비스 사용량 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
        raise Exception(f"AI Vision 오류: {error_msg[:150]}")


def call_gemini_api(prompt: str, image_base64: str = None) -> str:
    """Gemini API 호출 (Vision용 폴백)"""
    import requests
    
    gemini_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
    if not gemini_key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다.")
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
    
    parts = [{"text": prompt}]
    if image_base64:
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_base64}})
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096}
    }
    
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 429:
        raise Exception("Gemini 사용량 한도 초과. 잠시 후 다시 시도해주세요.")
    elif response.status_code != 200:
        raise Exception(f"Gemini API 오류: {response.text[:100]}")
    
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']


def call_huggingface_vision(prompt: str, image_base64: str) -> str:
    """Hugging Face Vision API 호출 (무료!)"""
    import requests
    
    hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')
    if not hf_token:
        raise ValueError("Hugging Face API 토큰이 설정되지 않았습니다.")
    
    # Llama-3.2-11B-Vision 모델 사용 (무료)
    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"
    
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    payload = {
        "inputs": {
            "image": image_base64,
            "text": prompt
        },
        "parameters": {"max_new_tokens": 2048}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 429:
        raise Exception("Hugging Face 사용량 한도 초과")
    elif response.status_code == 503:
        raise Exception("모델 로딩 중입니다. 잠시 후 다시 시도해주세요.")
    elif response.status_code != 200:
        raise Exception(f"Hugging Face 오류: {response.text[:100]}")
    
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '')
    return str(result)


def call_ai(prompt: str, image_base64: str = None) -> str:
    """통합 AI 호출 함수
    - Vision: Hugging Face → Gemini 폴백
    - 텍스트: Groq → Gemini 폴백
    """
    if image_base64:
        # Vision: Hugging Face 우선
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')
        if hf_token:
            try:
                return call_huggingface_vision(prompt, image_base64)
            except Exception as e:
                print(f"Hugging Face Vision 실패: {e}, Gemini로 폴백")
        
        # Gemini 폴백
        gemini_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
        if gemini_key:
            return call_gemini_api(prompt, image_base64)
        
        raise ValueError("이미지 분석을 위해 HUGGINGFACE_API_TOKEN 또는 GOOGLE_GEMINI_API_KEY가 필요합니다.")
    
    # 텍스트: Groq 우선
    client = get_groq_client()
    if client:
        return call_groq_text(prompt)
    
    # Gemini 폴백
    gemini_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
    if gemini_key:
        return call_gemini_api(prompt, None)
    
    raise ValueError("AI API 키가 설정되지 않았습니다.")


def process_image_for_ai(image_file) -> str:
    """이미지 전처리 후 Base64 반환"""
    image_file.seek(0)
    pil_image = PILImage.open(image_file)
    
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    max_size = 1024
    if pil_image.width > max_size or pil_image.height > max_size:
        pil_image.thumbnail((max_size, max_size), PILImage.Resampling.LANCZOS)
    
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG', quality=80, optimize=True)
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode('utf-8')


def match_to_master(name: str) -> tuple:
    """재료명을 마스터 데이터와 매칭"""
    master = find_master_by_name(name)
    if master:
        return master.name, master, master.category
    else:
        return name, None, '기타'


def parse_json_response(raw_text: str) -> list:
    """AI 응답에서 JSON 추출"""
    clean_json = re.sub(r'```json\s*|\s*```', '', raw_text)
    try:
        return json.loads(clean_json)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', clean_json, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return []


def analyze_receipt(image_file) -> dict:
    """영수증 이미지 분석"""
    prompt = """이 영수증 이미지에서 구매한 식재료/식품 목록을 추출해주세요.

다음 규칙을 따라주세요:
1. 식재료/식품만 추출 (비식품 제외)
2. 브랜드명 제거 (예: "풀무원 두부" → "두부")
3. 수량과 단위 포함
4. JSON 배열로만 응답 (다른 설명 없이)

응답 형식:
[
  {"name": "재료명", "quantity": 숫자, "unit": "단위"},
  ...
]
"""
    
    try:
        image_base64 = process_image_for_ai(image_file)
        raw_text = call_ai(prompt, image_base64)
        items_data = parse_json_response(raw_text)
        
        final_items = []
        for item in items_data:
            raw_name = item.get('name', '').strip()
            if not raw_name:
                continue
            
            name, master, category = match_to_master(raw_name)
            defaults = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS['기타'])
            
            final_items.append({
                'name': name,
                'category': category,
                'quantity': float(item.get('quantity', 1)),
                'unit': item.get('unit', master.default_unit if master else '개'),
                'icon': master.icon if master else defaults['icon'],
                'storage_method': defaults['storage'],
                'expiry_date': (date.today() + timedelta(days=defaults['days'])).strftime('%Y-%m-%d'),
            })
        
        return {'message': f'인식 완료 ({len(final_items)}개)', 'items': final_items}
        
    except Exception as e:
        raise Exception(f"영수증 분석 실패: {str(e)}")


def identify_ingredients_from_image(image_file) -> dict:
    """일반 사진에서 식재료 인식"""
    prompt = """이 사진에서 보이는 모든 식재료를 찾아 JSON 배열로 응답해주세요.
다른 설명 없이 JSON만 출력하세요.

응답 형식:
[
  {"name": "식재료명", "quantity": 숫자, "unit": "단위"},
  ...
]
"""
    
    try:
        image_base64 = process_image_for_ai(image_file)
        raw_text = call_ai(prompt, image_base64)
        items_data = parse_json_response(raw_text)
        
        merged = {}
        for item in items_data:
            raw_name = item.get('name', '').strip()
            if not raw_name:
                continue
            
            name, master, category = match_to_master(raw_name)
            defaults = CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS['기타'])
            qty = float(item.get('quantity', 1))
            
            if name in merged:
                merged[name]['quantity'] += qty
            else:
                merged[name] = {
                    'name': name,
                    'category': category,
                    'quantity': qty,
                    'unit': item.get('unit', master.default_unit if master else '개'),
                    'icon': master.icon if master else defaults['icon'],
                    'image_url': master.image_url if master else None,
                    'storage_method': defaults['storage'],
                    'expiry_date': (date.today() + timedelta(days=defaults['days'])).strftime('%Y-%m-%d'),
                    'is_ai_identified': True
                }
        
        return {'message': f'AI 분석 완료 ({len(merged)}개 식별)', 'items': list(merged.values())}
        
    except Exception as e:
        raise Exception(f"식재료 인식 실패: {str(e)}")
