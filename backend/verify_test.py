import os
import django
import json

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient

def verify():
    # 첫 번째 레시피 가져오기
    recipe = Recipe.objects.first()
    if not recipe:
        print("No recipes found.")
        return

    ingredients = list(RecipeIngredient.objects.filter(recipe=recipe).values_list('name', flat=True))
    
    result = {
        "title": recipe.title,
        "ingredients": ingredients
    }
    
    # UTF-8로 저장
    with open('verification_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Verification script completed for: {recipe.title}")

if __name__ == "__main__":
    verify()
