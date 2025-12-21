"""
레시피 재료 DB 정리 스크립트
GMS API를 활용하여 레시피 조리법을 분석하고 실제 필요한 재료를 추출합니다.
"""

import os
import sys
import json
import time
import requests
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from recipes.models import Recipe, RecipeIngredient, CookingStep

GMS_KEY = settings.GMS_KEY

def backup_ingredients():
    """기존 재료 데이터 백업"""
    backup_data = []
    for ri in RecipeIngredient.objects.all():
        backup_data.append({
            'recipe_id': ri.recipe_id,
            'recipe_title': ri.recipe.title,
            'name': ri.name,
            'quantity': ri.quantity
        })
    
    with open('recipe_ingredients_backup.json', 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 백업 완료: {len(backup_data)}개 재료 → recipe_ingredients_backup.json")
    return backup_data

def extract_ingredients_with_ai(recipe):
    """GMS API를 활용하여 레시피에서 실제 필요한 재료 추출"""
    
    # 조리 단계 텍스트 수집
    steps_text = "\n".join([
        f"{step.step_number}. {step.description}" 
        for step in recipe.steps.all().order_by('step_number')
    ])
    
    prompt = f"""다음 레시피의 조리법을 읽고, 실제로 필요한 재료만 추출해주세요.

레시피명: {recipe.title}
설명: {recipe.description or ''}

조리법:
{steps_text}

규칙:
1. 조리법에 실제로 언급된 재료만 추출
2. 각 재료는 순수한 재료명만 (단위, 숫자, 특수문자 제외)
3. 예: "소금 1큰술" → "소금", "다진 마늘 2스푼" → "마늘"
4. 조미료, 양념도 포함
5. "물"은 제외

JSON 형식으로 응답해주세요:
{{"ingredients": ["재료1", "재료2", "재료3", ...]}}
"""

    url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GMS_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        ai_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # JSON 파싱
        json_start = ai_text.find('{')
        json_end = ai_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = ai_text[json_start:json_end]
            data = json.loads(json_str)
            ingredients = data.get('ingredients', [])
            
            # 재료명 정제
            cleaned = []
            for ing in ingredients:
                # 공백 제거, 특수문자 제거
                name = ing.strip()
                # 숫자로 시작하면 제외
                if name and not name[0].isdigit() and len(name) >= 1:
                    # 단위 키워드 제거
                    skip_keywords = ['큰술', '작은술', '스푼', '컵', '개', 'g', 'ml', 'kg', '조금', '약간', '적당량']
                    is_unit = any(kw == name for kw in skip_keywords)
                    if not is_unit and len(name) <= 20:  # 너무 긴 건 제외
                        cleaned.append(name)
            
            return list(set(cleaned))  # 중복 제거
        
        return []
        
    except Exception as e:
        print(f"  ❌ AI 오류: {e}")
        return []

def process_all_recipes():
    """모든 레시피 처리"""
    
    if not GMS_KEY:
        print("❌ GMS_KEY 환경변수가 설정되지 않았습니다!")
        return
    
    # 1. 백업
    print("\n📦 1. 기존 재료 데이터 백업...")
    backup_ingredients()
    
    # 2. 기존 재료 삭제
    print("\n🗑️ 2. 기존 재료 데이터 초기화...")
    deleted_count = RecipeIngredient.objects.all().count()
    RecipeIngredient.objects.all().delete()
    print(f"  삭제됨: {deleted_count}개")
    
    # 3. 각 레시피 처리
    recipes = Recipe.objects.all().prefetch_related('steps')
    total = recipes.count()
    print(f"\n🔄 3. AI로 재료 추출 중... (총 {total}개 레시피)")
    
    success_count = 0
    fail_count = 0
    
    for i, recipe in enumerate(recipes, 1):
        print(f"\n[{i}/{total}] {recipe.title[:30]}...")
        
        # 조리 단계가 없으면 건너뛰기
        if not recipe.steps.exists():
            print("  ⚠️ 조리 단계 없음, 건너뜀")
            fail_count += 1
            continue
        
        # AI로 재료 추출
        ingredients = extract_ingredients_with_ai(recipe)
        
        if ingredients:
            # DB에 저장
            for name in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=name,
                    quantity="적당량"  # 기본값
                )
            print(f"  ✅ {len(ingredients)}개 재료: {', '.join(ingredients[:5])}{'...' if len(ingredients) > 5 else ''}")
            success_count += 1
        else:
            print("  ⚠️ 재료 추출 실패")
            fail_count += 1
        
        # API 레이트 리밋 방지
        time.sleep(0.5)
    
    print(f"\n" + "="*50)
    print(f"✅ 완료! 성공: {success_count}, 실패: {fail_count}")
    print(f"📁 백업 파일: recipe_ingredients_backup.json")

if __name__ == '__main__':
    print("="*50)
    print("🍳 레시피 재료 DB 정리 스크립트")
    print("="*50)
    
    confirm = input("\n⚠️ 기존 재료 데이터가 삭제됩니다. 계속하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        process_all_recipes()
    else:
        print("취소되었습니다.")
