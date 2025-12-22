# -*- coding: utf-8 -*-
"""
아이콘 재정비 스크립트
- 이모지가 정확히 일치하는 재료는 이모지 우선
- 그 외에는 media/ingredient_icons 이미지 사용
- 둘 다 없으면 카테고리별 기본 이모지
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

# 이모지가 정확히 일치하는 재료 목록 (파이썬에서 완벽하게 지원되는 이모지)
PERFECT_EMOJI_MAP = {
    # 과일
    "사과": "🍎",
    "빨간사과": "🍎",
    "풋사과": "🍏",
    "바나나": "🍌",
    "포도": "🍇",
    "청포도": "🍇",
    "수박": "🍉",
    "귤": "🍊",
    "오렌지": "🍊",
    "레몬": "🍋",
    "라임": "🍋",
    "망고": "🥭",
    "파인애플": "🍍",
    "코코넛": "🥥",
    "키위": "🥝",
    "토마토": "🍅",
    "방울토마토": "🍅",
    "복숭아": "🍑",
    "체리": "🍒",
    "딸기": "🍓",
    "블루베리": "🫐",
    "멜론": "🍈",
    "배": "🍐",
    "서양배": "🍐",
    
    # 채소
    "옥수수": "🌽",
    "고구마": "🍠",
    "단호박": "🎃",
    "호박": "🎃",
    "브로콜리": "🥦",
    "마늘": "🧄",
    "양파": "🧅",
    "감자": "🥔",
    "당근": "🥕",
    "오이": "🥒",
    "피클": "🥒",
    "가지": "🍆",
    "고추": "🌶️",
    "청양고추": "🌶️",
    "피망": "🫑",
    "파프리카": "🫑",
    "상추": "🥬",
    "양배추": "🥬",
    "배추": "🥬",
    "청경채": "🥬",
    "시금치": "🥬",
    "버섯": "🍄",
    "양송이버섯": "🍄",
    "새송이버섯": "🍄",
    "팽이버섯": "🍄",
    "표고버섯": "🍄",
    "느타리버섯": "🍄",
    "아보카도": "🥑",
    "올리브": "🫒",
    "콩나물": "🌱",
    "숙주": "🌱",
    "숙주나물": "🌱",
    
    # 육류/해산물
    "소고기": "🥩",
    "스테이크": "🥩",
    "등심": "🥩",
    "안심": "🥩",
    "불고기": "🥩",
    "돼지고기": "🥓",
    "삼겹살": "🥓",
    "베이컨": "🥓",
    "닭고기": "🍗",
    "닭": "🍗",
    "닭다리": "🍗",
    "치킨": "🍗",
    "새우": "🦐",
    "랍스터": "🦞",
    "게": "🦀",
    "꽃게": "🦀",
    "오징어": "🦑",
    "문어": "🐙",
    "생선": "🐟",
    "연어": "🐟",
    "참치": "🐟",
    "고등어": "🐟",
    "굴": "🦪",
    
    # 유제품/계란
    "계란": "🥚",
    "달걀": "🥚",
    "메추리알": "🥚",
    "우유": "🥛",
    "치즈": "🧀",
    "버터": "🧈",
    
    # 가공식품/기타
    "빵": "🍞",
    "식빵": "🍞",
    "바게트": "🥖",
    "크루아상": "🥐",
    "프레첼": "🥨",
    "팬케이크": "🥞",
    "와플": "🧇",
    "쌀": "🍚",
    "밥": "🍚",
    "국수": "🍜",
    "라면": "🍜",
    "스파게티": "🍝",
    "파스타": "🍝",
    "피자": "🍕",
    "햄버거": "🍔",
    "핫도그": "🌭",
    "타코": "🌮",
    "샌드위치": "🥪",
    "두부": "🧈",
    "땅콩": "🥜",
    "밤": "🌰",
    "꿀": "🍯",
    "소금": "🧂",
    "소스": "🥫",
    "케첩": "🥫",
    "통조림": "🥫",
    "아이스크림": "🍦",
    "초콜릿": "🍫",
    "사탕": "🍬",
    "쿠키": "🍪",
    "케이크": "🎂",
    "도넛": "🍩",
    "컵케이크": "🧁",
    "커피": "☕",
    "차": "🍵",
    "녹차": "🍵",
    "주스": "🧃",
    "와인": "🍷",
    "맥주": "🍺",
    "음료": "🥤",
    "물": "💧",
}

# 카테고리별 기본 이모지
CATEGORY_DEFAULT_EMOJI = {
    "채소": "🥬",
    "과일": "🍎",
    "육류": "🥩",
    "수산물": "🐟",
    "유제품": "🥛",
    "가공식품": "🥫",
    "곡류": "🌾",
    "음료": "🧃",
    "조미료": "🧂",
    "양념": "🧂",
    "기타": "📦",
}


def fix_all_icons():
    """모든 재료 아이콘 재정비"""
    # 미디어 폴더 내 이미지 목록
    icon_dir = os.path.join(os.path.dirname(__file__), 'media', 'ingredient_icons')
    available_images = {}
    if os.path.exists(icon_dir):
        for f in os.listdir(icon_dir):
            if f.lower().endswith('.png'):
                name = os.path.splitext(f)[0]
                available_images[name] = f
    
    print(f"사용 가능한 이미지 파일: {len(available_images)}개")
    
    all_masters = IngredientMaster.objects.all()
    
    count_emoji = 0
    count_image = 0
    count_default = 0
    changes_log = []
    
    for master in all_masters:
        old_icon = master.icon
        old_image = master.image_url
        
        # 1. 완벽한 이모지 매칭이 있는 경우 -> 이모지 우선
        if master.name in PERFECT_EMOJI_MAP:
            master.icon = PERFECT_EMOJI_MAP[master.name]
            master.image_url = None  # 이미지 URL 제거 (이모지 우선)
            count_emoji += 1
            if old_icon != master.icon or old_image != master.image_url:
                changes_log.append(f"[이모지] {master.name}: {old_icon} -> {master.icon}")
        
        # 2. 이미지가 있는 경우 -> 이미지 사용
        elif master.name in available_images:
            master.image_url = f"/media/ingredient_icons/{available_images[master.name]}"
            # 이모지도 카테고리별 기본값 설정
            master.icon = CATEGORY_DEFAULT_EMOJI.get(master.category, "📦")
            count_image += 1
            if old_image != master.image_url:
                changes_log.append(f"[이미지] {master.name}: {old_image} -> {master.image_url}")
        
        # 3. 부분 매칭 이모지 (재료명에 키워드가 포함된 경우)
        else:
            found_emoji = None
            for keyword, emoji in PERFECT_EMOJI_MAP.items():
                if keyword in master.name or master.name in keyword:
                    found_emoji = emoji
                    break
            
            if found_emoji:
                master.icon = found_emoji
                master.image_url = None
                count_emoji += 1
                if old_icon != master.icon:
                    changes_log.append(f"[부분이모지] {master.name}: {old_icon} -> {master.icon}")
            
            # 4. 부분 매칭 이미지
            else:
                found_image = None
                for img_name, img_file in available_images.items():
                    if img_name in master.name or master.name in img_name:
                        found_image = img_file
                        break
                
                if found_image:
                    master.image_url = f"/media/ingredient_icons/{found_image}"
                    master.icon = CATEGORY_DEFAULT_EMOJI.get(master.category, "📦")
                    count_image += 1
                    if old_image != master.image_url:
                        changes_log.append(f"[부분이미지] {master.name}: {old_image} -> {master.image_url}")
                
                # 5. 아무것도 없으면 카테고리별 기본 이모지
                else:
                    master.icon = CATEGORY_DEFAULT_EMOJI.get(master.category, "📦")
                    master.image_url = None
                    count_default += 1
        
        master.save()
    
    print(f"\n=== 아이콘 재정비 완료 ===")
    print(f"이모지 적용: {count_emoji}개")
    print(f"이미지 적용: {count_image}개")
    print(f"기본 아이콘: {count_default}개")
    print(f"\n변경된 항목 ({len(changes_log)}개):")
    for log in changes_log[:30]:
        print(f"  {log}")
    if len(changes_log) > 30:
        print(f"  ... 외 {len(changes_log) - 30}개")


if __name__ == "__main__":
    fix_all_icons()
