#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
로컬 DB 데이터를 JSON으로 export하는 스크립트
"""
import os
import sys
import django
import json

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
from recipes.models import Recipe, RecipeIngredient, CookingStep

def export_master_ingredients():
    """마스터 식재료 데이터 export"""
    print("[1/4] Exporting Master Ingredients...")
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
    """레시피 데이터 export"""
    print("[2/4] Exporting Recipes...")
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
                'author': None,  # 배포 환경에서는 author 없음 (외래키 문제 방지)
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
    print("[3/4] Exporting Recipe Ingredients...")
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
    print("[4/4] Exporting Recipe Steps...")
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
    # fixtures 디렉토리 생성
    os.makedirs('fixtures', exist_ok=True)
    
    try:
        export_master_ingredients()
        export_recipes()
        export_recipe_ingredients()
        export_recipe_steps()
        print("\n[SUCCESS] All data exported successfully!")
        print("[INFO] Check the 'fixtures' folder")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
