import os
import django
import json

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient

def check_data():
    # 1. 재료 데이터 검증 (랜덤하게 5개 샘플링)
    print("--- [1] 재료 데이터 정규화 확인 (랜덤 5개) ---")
    samples = Recipe.objects.all().order_by('?')[:5]
    for r in samples:
        ings = list(RecipeIngredient.objects.filter(recipe=r).values_list('name', flat=True))
        print(f"레시피: {r.title}")
        print(f"재료: {', '.join(ings)}")
        print("-" * 30)

    # 2. 이미지 없는 레시피 현황 확인
    no_image_recipes = Recipe.objects.filter(image_url__isnull=True) | Recipe.objects.filter(image_url='')
    no_image_count = no_image_recipes.count()
    total_count = Recipe.objects.count()
    print(f"\n--- [2] 이미지 현황 ---")
    print(f"총 레시피: {total_count}개")
    print(f"이미지 없는 레시피: {no_image_count}개")
    for r in no_image_recipes:
        print(f"ID: {r.id}, Title: {r.title}")

    # 결과 요약 저장
    summary = {
        "total": total_count,
        "no_image": no_image_count,
        "no_image_list": [{"id": r.id, "title": r.title} for r in no_image_recipes],
        "samples": [
            {"title": r.title, "ingredients": list(RecipeIngredient.objects.filter(recipe=r).values_list('name', flat=True))}
            for r in samples
        ]
    }
    with open('data_check_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    check_data()
