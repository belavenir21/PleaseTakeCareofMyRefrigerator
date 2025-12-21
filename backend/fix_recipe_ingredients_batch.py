"""
레시피 재료 DB 정리 스크립트 (배치 버전)
한번에 모든 레시피를 처리하지 않고, 배치 단위로 처리합니다.
사용법: python fix_recipe_ingredients_batch.py [시작인덱스] [배치크기]
예: python fix_recipe_ingredients_batch.py 0 50
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
from recipes.models import Recipe, RecipeIngredient

GMS_KEY = settings.GMS_KEY

def extract_ingredients_with_ai(recipe):
    """GMS API를 활용하여 레시피에서 실제 필요한 재료 추출"""
    
    steps_text = "\n".join([
        f"{step.step_number}. {step.description}" 
        for step in recipe.steps.all().order_by('step_number')
    ])
    
    prompt = f"""다음 레시피의 조리법을 읽고, 실제로 필요한 재료만 추출해주세요.

레시피명: {recipe.title}

조리법:
{steps_text}

규칙:
1. 조리법에 실제로 언급된 재료만 추출
2. 각 재료는 순수한 재료명만 (단위, 숫자, 특수문자 제외)
3. 예: "소금 1큰술" → "소금"
4. 물은 제외

JSON 형식으로만 응답:
{{"ingredients": ["재료1", "재료2"]}}
"""

    url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GMS_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        ai_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        json_start = ai_text.find('{')
        json_end = ai_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            data = json.loads(ai_text[json_start:json_end])
            ingredients = data.get('ingredients', [])
            
            cleaned = []
            for ing in ingredients:
                name = ing.strip()
                if name and not name[0].isdigit() and 1 <= len(name) <= 15:
                    cleaned.append(name)
            
            return list(set(cleaned))
        
        return []
        
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return []

def process_batch(start_idx, batch_size):
    """배치 처리"""
    
    if not GMS_KEY:
        print("❌ GMS_KEY가 설정되지 않았습니다!")
        return
    
    recipes = list(Recipe.objects.all().prefetch_related('steps', 'ingredients').order_by('id'))
    total = len(recipes)
    end_idx = min(start_idx + batch_size, total)
    
    print(f"\n🔄 배치 처리: {start_idx+1} ~ {end_idx} / {total}")
    
    for i in range(start_idx, end_idx):
        recipe = recipes[i]
        print(f"[{i+1}/{total}] {recipe.title[:25]}...", end=" ")
        
        if not recipe.steps.exists():
            print("⚠️ 단계 없음")
            continue
        
        # 기존 재료 삭제
        recipe.ingredients.all().delete()
        
        # AI로 추출
        ingredients = extract_ingredients_with_ai(recipe)
        
        if ingredients:
            for name in ingredients:
                RecipeIngredient.objects.create(recipe=recipe, name=name, quantity="적당량")
            print(f"✅ {len(ingredients)}개")
        else:
            print("⚠️ 실패")
        
        time.sleep(1)  # API 레이트 리밋 방지
    
    print(f"\n✅ 배치 완료! 다음 배치: python fix_recipe_ingredients_batch.py {end_idx} {batch_size}")

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    print("="*50)
    print("🍳 레시피 재료 정리 (배치)")
    print("="*50)
    
    process_batch(start, batch)
