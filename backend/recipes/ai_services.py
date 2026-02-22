"""
레시피 AI 서비스 모듈
AI 챗봇, 레시피 자동 생성 등
Groq 공식 라이브러리 사용
"""
import json
import re
from django.conf import settings

from .models import Recipe, RecipeIngredient, CookingStep
from master.models import find_master_by_name


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


def call_ai(prompt: str) -> str:
    """통합 AI 호출 함수 - Groq 공식 라이브러리"""
    client = get_groq_client()
    
    if client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4096
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                raise Exception("AI 서비스 사용량 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
            raise Exception(f"AI API 오류: {error_msg[:150]}")
    
    # Gemini 폴백
    gemini_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
    if gemini_key:
        import requests
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}'
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
        }
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 429:
            raise Exception("AI 서비스 사용량 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
        elif response.status_code != 200:
            raise Exception(f"AI API 오류 ({response.status_code}): {response.text[:150]}")
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    
    raise ValueError("AI API 키가 설정되지 않았습니다. GROQ_API_KEY 또는 GOOGLE_GEMINI_API_KEY를 설정해주세요.")


def generate_recipe_with_ai(recipe_name: str, user=None) -> Recipe:
    """AI로 레시피 자동 생성"""
    prompt = f"""다음 요리의 레시피를 JSON 형식으로 작성해주세요: "{recipe_name}"

다음 형식을 정확히 따라주세요:
{{
  "title": "요리명",
  "description": "간단한 설명",
  "cooking_time": 30,
  "difficulty": "쉬움/보통/어려움 중 하나",
  "category": "한식/중식/일식/양식/디저트/샐러드/퓨전/기타 중 하나",
  "ingredients": [
    {{"name": "재료명", "amount": "분량"}},
    ...
  ],
  "steps": [
    {{"description": "조리 단계 설명", "time_minutes": 5}},
    ...
  ]
}}

JSON만 출력하고 다른 설명은 하지 마세요.
"""
    
    try:
        raw_text = call_ai(prompt)
        
        # JSON 파싱
        clean_json = re.sub(r'```json\s*|\s*```', '', raw_text)
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                raise ValueError("AI 응답에서 JSON을 찾을 수 없습니다.")
        
        # 레시피 생성
        recipe = Recipe.objects.create(
            title=data.get('title', recipe_name),
            description=data.get('description', ''),
            cooking_time=data.get('cooking_time', 30),
            difficulty=data.get('difficulty', '보통'),
            category=data.get('category', '기타'),
            source='ai',
            author=user
        )
        
        # 재료 생성
        for ing in data.get('ingredients', []):
            name = ing.get('name', '').strip()
            if not name:
                continue
            
            master = find_master_by_name(name)
            
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=master.name if master else name,
                master=master,
                amount=ing.get('amount', '')
            )
        
        # 조리 단계 생성
        for idx, step in enumerate(data.get('steps', []), 1):
            CookingStep.objects.create(
                recipe=recipe,
                step_number=idx,
                description=step.get('description', ''),
                time_minutes=step.get('time_minutes', 0),
                icon=''
            )
        
        return recipe
        
    except Exception as e:
        raise Exception(f"레시피 생성 실패: {str(e)}")


def get_chatbot_response(message: str, user=None, include_ingredients: bool = False) -> dict:
    """AI 챗봇 응답 생성"""
    from refrigerator.models import UserIngredient
    from accounts.models import UserProfile
    
    context_info = ""
    user_ingredients = []
    allergies = []
    
    if user and include_ingredients:
        user_ings = UserIngredient.objects.filter(user=user, is_deleted=False)
        user_ingredients = [ui.name for ui in user_ings]
        context_info += f"\n[사용자의 냉장고 재료]: {', '.join(user_ingredients)}"
    
    if user:
        try:
            profile = UserProfile.objects.get(user=user)
            allergies = [a.name for a in profile.allergies.all()]
            diet_goals = profile.diet_goals or ''
            
            if allergies:
                context_info += f"\n[알레르기 주의]: {', '.join(allergies)}"
            if diet_goals:
                context_info += f"\n[식단 목표]: {diet_goals}"
        except UserProfile.DoesNotExist:
            pass
    
    system_prompt = """당신의 이름은 '쿠킹 미미'입니다! 🍳✨ 
밝고 친근한 요리 도우미로, 마치 요리 잘하는 친한 친구처럼 대화해주세요.

성격:
- 반말로 친근하게! (예: "이거 완전 맛있어!", "해볼래?")
- 이모지를 자주 사용해서 귀엽게! 😋🥰
- 열정적이고 신나는 말투!
- 짧고 간결하게 핵심만!

레시피 추천할 때:
🍳 **요리 이름**
📝 재료: (간단히)
👨‍🍳 조리법: (쉽게 설명)
💡 미미's 팁: (꿀팁!)

예시 답변:
"오~ 냉장고에 계란이랑 파 있구나? 🥚🌿 그럼 계란말이 어때? 완전 간단한데 맛있어!"
"""
    
    full_prompt = system_prompt + context_info + f"\n\n사용자 질문: {message}"
    
    try:
        ai_response = call_ai(full_prompt)
        
        return {
            'message': ai_response,
            'context': {
                'ingredients_used': user_ingredients if include_ingredients else [],
                'allergies_considered': allergies,
            }
        }
    except Exception as e:
        return {
            'message': f"죄송합니다, 응답을 생성하지 못했습니다: {str(e)}",
            'context': {}
        }
