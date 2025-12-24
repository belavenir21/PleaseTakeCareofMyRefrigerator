import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import Recipe, RecipeIngredient
from refrigerator.models import UserIngredient
from django.contrib.auth.models import User

# 계란 토스트 찾기
recipe = Recipe.objects.filter(title__contains='계란').filter(title__contains='토스트').first()
if not recipe:
    recipe = Recipe.objects.filter(title__contains='토스트').first()

if not recipe:
    print("Recipe not found!")
    exit()

print(f"Recipe: {recipe.title}")

# 레시피 재료
recipe_ings = RecipeIngredient.objects.filter(recipe=recipe)
print(f"\nRecipe ingredients ({recipe_ings.count()}):")
for ing in recipe_ings:
    print(f"  - {ing.name}")

# yushi 재료
yushi = User.objects.get(username='yushi')
user_ings = UserIngredient.objects.filter(user=yushi)
user_names = set(ui.name.replace(" ", "").lower() for ui in user_ings)

print(f"\nSearching for matches:")
recipe_unique = set(ri.name.replace(" ", "").lower() for ri in recipe_ings)
matched = []

# 동의어 함수
def get_variants(name):
    name = name.replace(" ", "")
    variants = [name]
    syns = {
        '달걀': '계란', '계란': '달걀', 
        '대파': '파', '파': '대파',
        '우유': '유유', '유유': '우유'
    }
    for k, v in syns.items():
        if k in name:
            variants.append(name.replace(k, v))
    return variants

for ring in recipe_unique:
    ring_variants = get_variants(ring)
    for uing in user_names:
        # 완전 일치만
        if uing in ring_variants or ring in get_variants(uing):
            matched.append(ring)
            break

print(f"\nResult:")
print(f"  Total: {len(recipe_unique)}")
print(f"  Matched: {len(matched)}")
print(f"  Ratio: {len(matched)}/{len(recipe_unique)} = {len(matched)/len(recipe_unique)*100:.1f}%")
print(f"\nMatched: {matched}")
print(f"Missing: {recipe_unique - set(matched)}")
