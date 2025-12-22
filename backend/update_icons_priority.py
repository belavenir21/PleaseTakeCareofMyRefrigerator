import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def update_priority_icons():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    
    # 이모지가 사진보다 훨씬 예쁘거나 정확한 '완벽 매칭' 리스트
    # 이 리스트에 있는 재료들은 image_url을 비우고 이모지만 사용함
    PERFECT_EMOJIS = {
        "계란": "🥚", "달걀": "🥚",
        "우유": "🥛",
        "사과": "🍎",
        "바나나": "🍌",
        "포도": "🍇",
        "수박": "🍉",
        "오렌지": "🍊", "귤": "🍊",
        "딸기": "🍓",
        "옥수수": "🌽",
        "당근": "🥕",
        "감자": "🥔",
        "고구마": "🍠",
        "마늘": "🧄",
        "양파": "🧅",
        "소금": "🧂",
        "후추": "🧂",
        "설탕": "🍬",
        "커피": "☕",
        "물": "💧",
        "빵": "🍞",
        "도넛": "🍩",
        "쿠키": "🍪",
        "맥주": "🍺",
        "와인": "🍷",
        "고기": "🥩",
        "생선": "🐟",
        "치즈": "🧀",
        "버터": "🧈",
        "꿀": "🍯",
        "소시지": "🌭",
        "베이컨": "🥓",
        "토마토": "🍅",
        "오이": "🥒",
        "브로콜리": "🥦",
        "버섯": "🍄",
        "레몬": "🍋"
    }

    # 전체 마스터 데이터 순회하며 우선순위 적용
    masters = IngredientMaster.objects.all()
    count_emoji = 0
    count_image = 0

    files = [os.path.splitext(f)[0] for f in os.listdir(base_dir) if f.endswith('.png')]

    for master in masters:
        # 1. 완벽 매칭 이모지 우선 적용
        is_perfect = False
        for key, emoji in PERFECT_EMOJIS.items():
            if key in master.name:
                master.icon = emoji
                master.image_url = None # 사진 대신 이모지 노출
                is_perfect = True
                count_emoji += 1
                break
        
        # 2. 이모지가 우선순위가 아니거나 매칭되지 않은 경우, 커스텀 이미지 찾기
        if not is_perfect:
            # 이름이 정확히 일치하는 파일 찾기
            matching_file = None
            if master.name in files:
                matching_file = f"{master.name}.png"
            else:
                # 부분 일치 파일 찾기
                for f in files:
                    if f in master.name:
                        matching_file = f"{f}.png"
                        break
            
            if matching_file:
                master.image_url = f"/media/ingredient_icons/{matching_file}"
                count_image += 1
            else:
                # 이미지도 없으면 기본 이모지라도 유지 (기본값 📦 등)
                if not master.icon:
                    master.icon = "📦"
        
        master.save()

    print(f"Priority Update Done!")
    print(f"Emoji-only (Perfect match): {count_emoji}")
    print(f"Image-based (Custom icon): {count_image}")

if __name__ == "__main__":
    update_priority_icons()
