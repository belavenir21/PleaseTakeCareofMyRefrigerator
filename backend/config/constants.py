"""
프로젝트 전역 상수 정의 - V2
순환 참조 방지를 위해 이 파일에서 직접 정의
"""

# ===== 식재료 카테고리 =====
INGREDIENT_CATEGORIES = [
    ('채소', '채소'),
    ('과일/견과', '과일/견과'),
    ('수산물', '수산물'),
    ('육류/달걀', '육류/달걀'),
    ('유제품', '유제품'),
    ('곡류', '곡류'),
    ('양념/오일', '양념/오일'),
    ('가공식품', '가공식품'),
    ('간편식', '간편식'),
    ('음료', '음료'),
    ('기타', '기타'),
]

INGREDIENT_CATEGORY_CHOICES = INGREDIENT_CATEGORIES

# ===== 보관 방법 =====
STORAGE_METHODS = [
    ('냉장', '냉장'),
    ('냉동', '냉동'),
    ('실온', '실온'),
]

# ===== 레시피 관련 =====
DIFFICULTY_CHOICES = [
    ('쉬움', '쉬움'),
    ('보통', '보통'),
    ('어려움', '어려움'),
]

RECIPE_CATEGORIES = [
    ('한식', '한식'),
    ('중식', '중식'),
    ('일식', '일식'),
    ('양식', '양식'),
    ('디저트', '디저트'),
    ('샐러드', '샐러드'),
    ('퓨전', '퓨전'),
    ('기타', '기타'),
]

RECIPE_CATEGORY_CHOICES = RECIPE_CATEGORIES

SOURCE_CHOICES = [
    ('api', 'API'),
    ('user', '사용자'),
    ('ai', 'AI 생성'),
]

# ===== 카테고리별 기본 설정 =====
CATEGORY_DEFAULTS = {
    '채소': {'storage': '냉장', 'days': 7, 'icon': '🥬'},
    '과일/견과': {'storage': '냉장', 'days': 10, 'icon': '🍎'},
    '수산물': {'storage': '냉동', 'days': 3, 'icon': '🐟'},
    '육류/달걀': {'storage': '냉장', 'days': 5, 'icon': '🥩'},
    '유제품': {'storage': '냉장', 'days': 10, 'icon': '🥛'},
    '곡류': {'storage': '실온', 'days': 90, 'icon': '🌾'},
    '양념/오일': {'storage': '실온', 'days': 180, 'icon': '🧂'},
    '가공식품': {'storage': '실온', 'days': 60, 'icon': '🥫'},
    '간편식': {'storage': '냉장', 'days': 14, 'icon': '🍱'},
    '음료': {'storage': '냉장', 'days': 30, 'icon': '🧃'},
    '기타': {'storage': '냉장', 'days': 14, 'icon': '📦'},
}

# 기본 유통기한 (일 단위)
DEFAULT_EXPIRY_DAYS = {
    cat[0]: CATEGORY_DEFAULTS[cat[0]]['days']
    for cat in INGREDIENT_CATEGORIES
}

# 기본 보관방법
DEFAULT_STORAGE_METHOD = {
    cat[0]: CATEGORY_DEFAULTS[cat[0]]['storage']
    for cat in INGREDIENT_CATEGORIES
}


def get_category_defaults(category: str) -> dict:
    """카테고리별 기본 설정 반환"""
    return CATEGORY_DEFAULTS.get(category, CATEGORY_DEFAULTS['기타'])


def normalize_category(category: str, category_type: str = 'ingredient') -> str:
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
    
    # 표준 카테고리 목록
    if category_type == 'ingredient':
        valid_categories = [c[0] for c in INGREDIENT_CATEGORIES]
    else:
        valid_categories = [c[0] for c in RECIPE_CATEGORIES]
    
    # 이미 표준 카테고리인지 확인
    if category in valid_categories:
        return category
    
    # 마이그레이션 맵 (구 카테고리 → 신 카테고리)
    migration_map = {
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
    
    # 마이그레이션 맵 확인
    if category in migration_map:
        return migration_map[category]
    
    # 부분 매칭
    category_lower = category.lower()
    for old, new in migration_map.items():
        if old.lower() in category_lower or category_lower in old.lower():
            return new
    
    return '기타'
