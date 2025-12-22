import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
from refrigerator.models import UserIngredient

def final_sync_and_priority():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    
    # 사용자님이 원하신 '기본 아이템은 이모지가 더 깔끔하다' 리스트
    PERFECT_EMOJIS = {
        "계란": "🥚", "달걀": "🥚", "메추리알": "🥚",
        "우유": "🥛", "요거트": "🍦",
        "사과": "🍎", "바나나": "🍌", "포도": "🍇", "수박": "🍉", 
        "딸기": "🍓", "오렌지": "🍊", "귤": "🍊", "레몬": "🍋", "키위": "🥝",
        "당근": "🥕", "감자": "🥔", "고구마": "🍠", "마늘": "🧄", "양파": "🧅",
        "소금": "🧂", "후추": "🧂", "설탕": "🍬", "커피": "☕", "물": "💧",
        "빵": "🍞", "도넛": "🍩", "쿠키": "🍪", "치즈": "🧀", "버터": "🧈",
        "고기": "🥩", "소고기": "🥩", "생선": "🐟", "새우": "🍤", "게": "🦀",
        "토마토": "🍅", "오이": "🥒", "브로콜리": "🥦", "버섯": "🍄", "가지": "🍆", "고추": "🌶️"
    }

    files = [os.path.splitext(f)[0] for f in os.listdir(base_dir) if f.lower().endswith('.png')]
    print(f"Total renamed icons found: {len(files)}")

    masters = IngredientMaster.objects.all()
    count_emoji = 0
    count_image = 0
    count_unlinked_fixed = 0

    for master in masters:
        # 1. 완벽 매칭 이모지 우선 (사용자 요청: 계란 등은 이모지가 더 예쁨)
        is_perfect = False
        for key, emoji in PERFECT_EMOJIS.items():
            if key == master.name: # 정확히 일치할 때만 이모지 우선
                master.icon = emoji
                master.image_url = None
                is_perfect = True
                count_emoji += 1
                break
        
        # 2. 이모지 우선순위가 아니면 사용자님이 이름 붙인 이미지 매칭
        if not is_perfect:
            # 파일명과 정확히 일치하거나, 파일명이 마스터 이름에 포함된 경우
            matching_file = None
            if master.name in files:
                matching_file = f"{master.name}.png"
            else:
                for f in files:
                    if f == master.name or (len(f) > 1 and f in master.name):
                        matching_file = f"{f}.png"
                        break
            
            if matching_file:
                master.image_url = f"/media/ingredient_icons/{matching_file}"
                # 이미지 이름 기반으로 간단 이모지도 보조로 넣어줌
                if not master.icon:
                    master.icon = "📦"
                count_image += 1
            else:
                # 둘 다 없으면 기본값
                if not master.icon:
                    master.icon = "📦"
                master.image_url = None

        master.save()

    # 3. 유저가 리스트에 직접 텍스트로 보관 중인 재료들도 마스터와 연결
    unlinked_ips = UserIngredient.objects.filter(master_ingredient__isnull=True)
    for up in unlinked_ips:
        # 이름으로 마스터 찾기
        best_master = IngredientMaster.objects.filter(name=up.name).first()
        if not best_master:
            best_master = IngredientMaster.objects.filter(name__icontains=up.name).first()
        
        if best_master:
            up.master_ingredient = best_master
            up.save()
            count_unlinked_fixed += 1

    print(f"\n--- Final Sync Complete ---")
    print(f"Enabled Emojis (Priority): {count_emoji}")
    print(f"Enabled Custom Images: {count_image}")
    print(f"Linked existing user ingredients to master: {count_unlinked_fixed}")

if __name__ == "__main__":
    final_sync_and_priority()
