"""
카테고리 통일 및 레시피 시간 수정 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
from refrigerator.models import UserIngredient
from recipes.models import Recipe, RecipeIngredient

# ===== 1. 마스터 카테고리 정의 (프로젝트 전체 통일) =====
MASTER_CATEGORIES = [
    '채소',
    '과일/견과',
    '수산물',
    '육류/달걀',
    '유제품',
    '곡류',
    '양념/오일',
    '가공식품',
    '간편식',
    '음료',
    '기타'
]

# ===== 2. 카테고리 매핑 (기존 → 표준화) =====
CATEGORY_MAPPING = {
    # 기존 카테고리 → 표준 카테고리
    '수산/건어물': '수산물',
    '간편식/식단': '간편식',
    '면/양념/오일': '양념/오일',
    '커피/차': '음료',
    # 다른 변형들도 추가 가능
    '채소류': '채소',
    '과일류': '과일/견과',
    '육류': '육류/달걀',
    '달걀': '육류/달걀',
    '견과': '과일/견과',
    '수산': '수산물',
    '건어물': '수산물',
    '면': '양념/오일',
    '양념': '양념/오일',
    '오일': '양념/오일',
    '가공': '가공식품',
    '간편': '간편식',
    '식단': '간편식',
}

def normalize_category(cat):
    """카테고리 정규화 (매핑 적용)"""
    if not cat:
        return '기타'
    
    cat = cat.strip()
    
    # 직접 매칭
    if cat in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[cat]
    
    # 표준 카테고리 그대로 사용
    if cat in MASTER_CATEGORIES:
        return cat
    
    # 부분 매칭 (예: "수산" 포함 시 "수산물"로)
    for old, new in CATEGORY_MAPPING.items():
        if old in cat or cat in old:
            return new
    
    # 모두 실패하면 기타
    return '기타'

def fix_ingredient_master_categories():
    """IngredientMaster 카테고리 통일"""
    print("\n=== 🔧 IngredientMaster 카테고리 수정 ===")
    
    ingredients = IngredientMaster.objects.all()
    updated = 0
    
    for ing in ingredients:
        old_cat = ing.category
        new_cat = normalize_category(old_cat)
        
        if old_cat != new_cat:
            ing.category = new_cat
            ing.save()
            updated += 1
            print(f"  ✅ {ing.name}: {old_cat} → {new_cat}")
    
    print(f"\n총 {updated}개 수정 완료!\n")

def fix_user_ingredient_categories():
    """UserIngredient 카테고리 통일 (master_ingredient 연결 기준)"""
    print("\n=== 🔧 UserIngredient 카테고리 수정 ===")
    
    user_ings = UserIngredient.objects.all()
    updated = 0
    
    for u_ing in user_ings:
        # master_ingredient가 있으면 그걸 기준으로
        if u_ing.master_ingredient:
            new_cat = u_ing.master_ingredient.category
            if u_ing.category != new_cat:
                u_ing.category = new_cat
                u_ing.save()
                updated += 1
                print(f"  ✅ {u_ing.name}: {u_ing.category} → {new_cat} (마스터 기준)")
        else:
            # master가 없으면 기존 값 정규화
            old_cat = u_ing.category or '기타'
            new_cat = normalize_category(old_cat)
            if old_cat != new_cat:
                u_ing.category = new_cat
                u_ing.save()
                updated += 1
                print(f"  ✅ {u_ing.name}: {old_cat} → {new_cat}")
    
    print(f"\n총 {updated}개 수정 완료!\n")

def fix_recipe_categories():
    """Recipe 카테고리 정리 (한식/중식/일식/양식/디저트 등만 적용)"""
    print("\n=== 🔧 Recipe 카테고리 확인 ===")
    
    # 레시피는 요리 장르이므로 식재료 카테고리와 별개
    # 하지만 잘못 입력된 경우 수정
    recipes = Recipe.objects.all()
    
    RECIPE_CATEGORIES = ['한식', '중식', '일식', '양식', '디저트', '샐러드', '퓨전', '기타']
    
    updated = 0
    for recipe in recipes:
        if recipe.category not in RECIPE_CATEGORIES:
            print(f"  ⚠️ {recipe.title}: '{recipe.category}' (비표준 카테고리)")
            # 자동 매핑이 어려우므로 '기타'로 설정
            recipe.category = '기타'
            recipe.save()
            updated += 1
    
    print(f"\n총 {updated}개 레시피 카테고리 수정 완료!\n")

def fix_recipe_cooking_time():
    """Recipe 조리시간 수정 (잘못된 데이터 정리)"""
    print("\n=== 🔧 Recipe 조리시간 검증 ===")
    
    recipes = Recipe.objects.all()
    fixed = 0
    
    for recipe in recipes:
        # 조리 시간이 비정상적으로 크거나 작은 경우 수정
        if recipe.cooking_time_minutes <= 0:
            print(f"  ⚠️ {recipe.title}: 조리시간 {recipe.cooking_time_minutes}분 → 30분으로 수정")
            recipe.cooking_time_minutes = 30
            recipe.save()
            fixed += 1
        elif recipe.cooking_time_minutes > 300:  # 5시간 이상은 비정상
            print(f"  ⚠️ {recipe.title}: 조리시간 {recipe.cooking_time_minutes}분 → 60분으로 수정")
            recipe.cooking_time_minutes = 60
            recipe.save()
            fixed += 1
    
    print(f"\n총 {fixed}개 레시피 시간 수정 완료!\n")

def verify_categories():
    """카테고리 통계 확인"""
    print("\n=== 📊 카테고리 검증 결과 ===")
    
    print("\n[IngredientMaster]")
    master_cats = IngredientMaster.objects.values_list('category', flat=True).distinct().order_by('category')
    for cat in master_cats:
        count = IngredientMaster.objects.filter(category=cat).count()
        status = "✅" if cat in MASTER_CATEGORIES else "❌"
        print(f"  {status} {cat}: {count}개")
    
    print("\n[UserIngredient]")
    user_cats = UserIngredient.objects.values_list('category', flat=True).distinct().order_by('category')
    for cat in user_cats:
        if cat:
            count = UserIngredient.objects.filter(category=cat).count()
            status = "✅" if cat in MASTER_CATEGORIES else "❌"
            print(f"  {status} {cat}: {count}개")
    
    print("\n[Recipe]")
    recipe_cats = Recipe.objects.values_list('category', flat=True).distinct().order_by('category')
    for cat in recipe_cats:
        count = Recipe.objects.filter(category=cat).count()
        print(f"  📗 {cat}: {count}개")

if __name__ == '__main__':
    print("🚀 카테고리 및 레시피 시간 수정 시작...\n")
    
    # STEP 1: IngredientMaster 수정
    fix_ingredient_master_categories()
    
    # STEP 2: UserIngredient 수정
    fix_user_ingredient_categories()
    
    # STEP 3: Recipe 카테고리 검증
    fix_recipe_categories()
    
    # STEP 4: Recipe 조리시간 검증
    fix_recipe_cooking_time()
    
    # STEP 5: 최종 검증
    verify_categories()
    
    print("\n✅ 모든 작업 완료!")
    print(f"\n📋 표준 카테고리 목록 ({len(MASTER_CATEGORIES)}개):")
    for i, cat in enumerate(MASTER_CATEGORIES, 1):
        print(f"  {i}. {cat}")
