#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway 배포용 fixtures 생성 (유저 포함)
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from master.models import IngredientMaster
from recipes.models import Recipe, RecipeIngredient, CookingStep

def export_users():
    """유저 export (비밀번호는 해시 그대로)"""
    print("[0/5] Exporting Users...")
    users = User.objects.all()
    
    data = []
    for user in users:
        data.append({
            'model': 'auth.user',
            'pk': user.id,
            'fields': {
                'username': user.username,
                'password': user.password,  # 해시된 비밀번호 그대로
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        })
    
    with open('fixtures/users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data)} users")

def export_master_ingredients():
    """마스터 식재료 데이터 export"""
    print("[1/5] Exporting Master Ingredients...")
    ingredients = IngredientMaster.objects.all()
    
    data = []
    for ing in ingredients:
        data.append({
            'model': 'master.ingredientmaster',
            'pk': ing.id,
            'fields': {
                'name': ing.name,
                'category': ing.category,
                'default_unit': ing.default_unit,
                'icon': ing.icon,
                'image_url': ing.image_url or '',
                'api_source': ing.api_source or '',
                'api_id': ing.api_id or '',
                'created_at': ing.created_at.isoformat() if ing.created_at else None,
                'updated_at': ing.updated_at.isoformat() if ing.updated_at else None,
            }
        })
    
    with open('fixtures/master_ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data)} master ingredients")

def export_recipes():
    """레시피 데이터 export (author 포함!)"""
    print("[2/5] Exporting Recipes...")
    recipes = Recipe.objects.all()
    
    data = []
    for recipe in recipes:
        data.append({
            'model': 'recipes.recipe',
            'pk': recipe.id,
            'fields': {
                'title': recipe.title,
                'description': recipe.description or '',
                'cooking_time_minutes': recipe.cooking_time_minutes,
                'difficulty': recipe.difficulty,
                'category': recipe.category or '',
                'image_url': recipe.image_url or '',
                'tags': recipe.tags if recipe.tags else [],
                'author': recipe.author_id if recipe.author else None,  # 원래대로!
                'api_source': recipe.api_source or '',
                'api_id': recipe.api_id or '',
                'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
                'updated_at': recipe.updated_at.isoformat() if recipe.updated_at else None,
            }
        })
    
    with open('fixtures/recipes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data)} recipes")

def export_recipe_ingredients():
    """레시피 재료 데이터 export"""
    print("[3/5] Exporting Recipe Ingredients...")
    ingredients = RecipeIngredient.objects.all()
    
    data = []
    for ing in ingredients:
        data.append({
            'model': 'recipes.recipeingredient',
            'pk': ing.id,
            'fields': {
                'recipe': ing.recipe_id,
                'name': ing.name,
                'quantity': ing.quantity or '',
            }
        })
    
    with open('fixtures/recipe_ingredients.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data)} recipe ingredients")

def export_recipe_steps():
    """레시피 조리 단계 export"""
    print("[4/5] Exporting Recipe Steps...")
    steps = CookingStep.objects.all()
    
    data = []
    for step in steps:
        data.append({
            'model': 'recipes.cookingstep',
            'pk': step.id,
            'fields': {
                'recipe': step.recipe_id,
                'step_number': step.step_number,
                'description': step.description,
                'time_minutes': step.time_minutes or 0,
            }
        })
    
    with open('fixtures/recipe_steps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(data)} recipe steps")

if __name__ == '__main__':
    os.makedirs('fixtures', exist_ok=True)
    
    try:
        export_users()  # 유저 먼저!
        export_master_ingredients()
        export_recipes()
        export_recipe_ingredients()
        export_recipe_steps()
        print("\n[SUCCESS] All data exported successfully!")
        print("[INFO] Check the 'fixtures' folder")
        print("\n[RAILWAY IMPORT ORDER]")
        print("1. railway run python manage.py loaddata fixtures/users.json")
        print("2. railway run python manage.py loaddata fixtures/master_ingredients.json")
        print("3. railway run python manage.py loaddata fixtures/recipes.json")
        print("4. railway run python manage.py loaddata fixtures/recipe_ingredients.json")
        print("5. railway run python manage.py loaddata fixtures/recipe_steps.json")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
