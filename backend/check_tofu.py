"""
두부까나페 매칭률 직접 계산
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient
from refrigerator.models import UserIngredient
from django.contrib.auth.models import User

# 두부까나페 찾기
recipe = Recipe.objects.filter(title__contains='두부까나페').first()
if not recipe:
    print("Recipe not found!")
    exit()

print(f"Recipe: {recipe.title}")
print(f"  ID: {recipe.id}")

# 레시피 재료
recipe_ings = RecipeIngredient.objects.filter(recipe=recipe)
print(f"\nRecipe ingredients (total: {recipe_ings.count()}):")
for ing in recipe_ings:
    print(f"  - {ing.name}")

# yushi 유저
yushi = User.objects.get(username='yushi')
user_ings = UserIngredient.objects.filter(user=yushi)
user_names = set(ui.name.replace(" ", "").lower() for ui in user_ings)

print(f"\nYushi's ingredients (total: {user_ings.count()}):")
print(f"  (showing first 20)")
for ui in list(user_ings)[:20]:
    print(f"  - {ui.name}")

# 매칭 계산
recipe_unique = set(ri.name.replace(" ", "").lower() for ri in recipe_ings)
matched = []
for ring in recipe_unique:
    for uing in user_names:
        if ring in uing or uing in ring:
            matched.append(ring)
            break

print(f"\nMatching calculation:")
print(f"  Recipe unique ingredients: {len(recipe_unique)}")
print(f"  User unique ingredients: {len(user_names)}")
print(f"  Matched: {len(matched)}")
print(f"  Match ratio: {len(matched)}/{len(recipe_unique)} = {len(matched)/len(recipe_unique)*100:.1f}%")

print(f"\nMatched ingredients:")
for m in matched:
    print(f"  - {m}")

print(f"\nMissing ingredients:")
missing = recipe_unique - set(matched)
for m in missing:
    print(f"  - {m}")
