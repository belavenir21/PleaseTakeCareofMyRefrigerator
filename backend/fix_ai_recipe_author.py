"""
AI 생성 레시피에 author 추가
"""
import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import Recipe
from django.contrib.auth.models import User

# ai_generated이면서 author가 null인 레시피들 찾기
ai_recipes_no_author = Recipe.objects.filter(api_source='ai_generated', author__isnull=True)

print(f"Found {ai_recipes_no_author.count()} AI recipes without author")

# yushi 유저
yushi = User.objects.get(username='yushi')

for recipe in ai_recipes_no_author:
    print(f"  Updating: {recipe.title} (ID: {recipe.id})")
    recipe.author = yushi
    recipe.save()
    print(f"    -> Author set to {yushi.username}")

# 확인
print("\n\nVerification:")
print(f"Total recipes by {yushi.username}: {Recipe.objects.filter(author=yushi).count()}")

# yushi의 모든 레시피 출력
yushi_recipes = Recipe.objects.filter(author=yushi)
for r in yushi_recipes:
    print(f"  - {r.title} (source: {r.api_source})")
