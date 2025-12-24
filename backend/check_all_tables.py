"""
모든 테이블 샘플 데이터 출력
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from master.models import IngredientMaster, AllergyMaster
from refrigerator.models import UserIngredient
from recipes.models import Recipe, RecipeIngredient, CookingStep

print("\n" + "="*80)
print("DATABASE TABLES OVERVIEW")
print("="*80)

# 1. User 테이블
print("\n[1] USER TABLE")
print("-" * 80)
users = User.objects.all()[:3]
print(f"Total Users: {User.objects.count()}")
for u in users:
    print(f"  ID: {u.id} | Username: {u.username} | Email: {u.email}")

# 2. UserProfile 테이블
print("\n[2] USER_PROFILE TABLE")
print("-" * 80)
from accounts.models import UserProfile
profiles = UserProfile.objects.all()[:3]
print(f"Total Profiles: {UserProfile.objects.count()}")
for p in profiles:
    print(f"  User: {p.user.username} | Nickname: {p.nickname} | Diet: {p.diet_goals}")

# 3. IngredientMaster 테이블
print("\n[3] INGREDIENT_MASTER TABLE")
print("-" * 80)
masters = IngredientMaster.objects.all()[:10]
print(f"Total Ingredient Masters: {IngredientMaster.objects.count()}")
for m in masters:
    print(f"  ID: {m.id} | Name: {m.name} | Category: {m.category} | Unit: {m.default_unit}")

# 4. UserIngredient 테이블 (가장 중요!)
print("\n[4] USER_INGREDIENT TABLE (보관함)")
print("-" * 80)
user_ings = UserIngredient.objects.all().order_by('-created_at')[:10]
print(f"Total User Ingredients: {UserIngredient.objects.count()}")
if user_ings:
    for ui in user_ings:
        print(f"  ID: {ui.id} | User: {ui.user.username} | Name: {ui.name} | "
              f"Qty: {ui.quantity}{ui.unit} | Category: {ui.category} | "
              f"Expiry: {ui.expiry_date} | Created: {ui.created_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print("  (No ingredients found)")

# 최근 추가된 재료 확인
print("\n[4-1] RECENTLY ADDED INGREDIENTS (Last 5)")
print("-" * 80)
recent = UserIngredient.objects.all().order_by('-created_at')[:5]
for r in recent:
    print(f"  {r.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {r.user.username} | {r.name} ({r.quantity}{r.unit})")

# 5. Recipe 테이블
print("\n[5] RECIPE TABLE")
print("-" * 80)
recipes = Recipe.objects.all()[:5]
print(f"Total Recipes: {Recipe.objects.count()}")
for r in recipes:
    print(f"  ID: {r.id} | Title: {r.title[:40]} | Time: {r.cooking_time_minutes}min | "
          f"Difficulty: {r.difficulty}")

# 6. RecipeIngredient 테이블
print("\n[6] RECIPE_INGREDIENT TABLE")
print("-" * 80)
recipe_ings = RecipeIngredient.objects.all()[:10]
print(f"Total Recipe Ingredients: {RecipeIngredient.objects.count()}")
for ri in recipe_ings:
    print(f"  Recipe: {ri.recipe.title[:30]} | Ingredient: {ri.name}")

# 7. CookingStep 테이블
print("\n[7] COOKING_STEP TABLE")
print("-" * 80)
steps = CookingStep.objects.all()[:5]
print(f"Total Cooking Steps: {CookingStep.objects.count()}")
for s in steps:
    print(f"  Recipe: {s.recipe.title[:30]} | Step {s.step_number}: {s.description[:50]}...")

# 8. AllergyMaster 테이블
print("\n[8] ALLERGY_MASTER TABLE")
print("-" * 80)
allergies = AllergyMaster.objects.all()
print(f"Total Allergies: {AllergyMaster.objects.count()}")
for a in allergies[:5]:
    print(f"  ID: {a.id} | Name: {a.name}")

print("\n" + "="*80)
print("END OF DATABASE OVERVIEW")
print("="*80 + "\n")

# 특정 사용자의 보관함 확인
print("\n[DETAILED CHECK: Latest User's Pantry]")
print("-" * 80)
latest_user = User.objects.order_by('-date_joined').first()
if latest_user:
    print(f"Checking user: {latest_user.username}")
    user_items = UserIngredient.objects.filter(user=latest_user).order_by('-created_at')
    print(f"Total items: {user_items.count()}")
    for item in user_items[:10]:
        print(f"  - {item.name} ({item.quantity}{item.unit}) | Expiry: {item.expiry_date} | "
              f"Storage: {item.storage_method}")
