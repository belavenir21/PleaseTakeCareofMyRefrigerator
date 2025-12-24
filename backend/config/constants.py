"""
프로젝트 전역 카테고리 상수 정의
모든 앱에서 이 파일을 import하여 카테고리를 통일
"""

# ===== 식재료 카테고리 (IngredientMaster, UserIngredient) =====
INGREDIENT_CATEGORIES = [
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

INGREDIENT_CATEGORY_CHOICES = [(cat, cat) for cat in INGREDIENT_CATEGORIES]

# ===== 레시피 카테고리 (Recipe) =====
RECIPE_CATEGORIES = [
    '한식',
    '중식',
    '일식',
    '양식',
    '디저트',
    '샐러드',
    '퓨전',
    '기타'
]

RECIPE_CATEGORY_CHOICES = [(cat, cat) for cat in RECIPE_CATEGORIES]

# ===== 카테고리 매핑 (기존 데이터 마이그레이션용) =====
CATEGORY_MIGRATION_MAP = {
    # 식재료 카테고리 변환
    '수산/건어물': '수산물',
    '간편식/식단': '간편식',
    '면/양념/오일': '양념/오일',
    '커피/차': '음료',
    '채소류': '채소',
    '과일류': '과일/견과',
    '육류': '육류/달걀',
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

def normalize_category(category, category_type='ingredient'):
    """
    카테고리 정규화 함수
    
    Args:
        category: 원본 카테고리 문자열
        category_type: 'ingredient' 또는 'recipe'
    
    Returns:
        정규화된 카테고리 문자열
    """
    if not category:
        return '기타'
    
    category = category.strip()
    
    # 이미 표준 카테고리인지 확인
    categories = INGREDIENT_CATEGORIES if category_type == 'ingredient' else RECIPE_CATEGORIES
    if category in categories:
        return category
    
    # 마이그레이션 맵 확인
    if category in CATEGORY_MIGRATION_MAP:
        return CATEGORY_MIGRATION_MAP[category]
    
    # 부분 매칭 (대소문자 무시)
    category_lower = category.lower()
    for old, new in CATEGORY_MIGRATION_MAP.items():
        if old.lower() in category_lower or category_lower in old.lower():
            return new
    
    # 모두 실패하면 기타
    return '기타'

# ===== 카테고리별 기본 유통기한 설정 (일 단위) =====
DEFAULT_EXPIRY_DAYS = {
    '채소': 7,
    '과일/견과': 10,
    '수산물': 3,
    '육류/달걀': 5,
    '유제품': 10,
    '곡류': 30,
    '양념/오일': 180,
    '가공식품': 60,
    '간편식': 14,
    '음료': 30,
    '기타': 14,
}

# ===== 카테고리별 기본 보관방법 =====
DEFAULT_STORAGE_METHOD = {
    '채소': '냉장',
    '과일/견과': '냉장',
    '수산물': '냉동',
    '육류/달걀': '냉장',
    '유제품': '냉장',
    '곡류': '실온',
    '양념/오일': '실온',
    '가공식품': '실온',
    '간편식': '냉장',
    '음료': '냉장',
    '기타': '냉장',
}
