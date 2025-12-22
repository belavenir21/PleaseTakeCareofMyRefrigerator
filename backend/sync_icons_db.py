import os
import django
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
from refrigerator.models import UserIngredient

def sync_renamed_icons():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    
    if not os.path.exists(base_dir):
        print(f"Directory not found: {base_dir}")
        return

    # 이모지 매칭 사전 (확장형)
    emoji_dict = {
        "소고기": "🥩", "등심": "🥩", "안심": "🥩", "불고기": "🥩",
        "삼겹살": "🥓", "돼지": "🐖", "제육": "🥓", "베이컨": "🥓",
        "닭": "🍗", "치킨": "🍗", "생닭": "🍗",
        "생선": "🐟", "연어": "🍣", "참치": "🐟", "고등어": "🐟", "갈치": "🐟",
        "두부": "⬜", "유부": "⬜",
        "배추": "🥬", "양배추": "🥬", "상추": "🥬", "깻잎": "🍃", "시금치": "🥬", "부추": "🌱",
        "청경채": "🥬", "채소": "🥗", "샐러드": "🥗",
        "무": "🍖", "당근": "🥕", "양파": "🧅", "마늘": "🧄", "대파": "🎋", "파": "🎋",
        "감자": "🥔", "고구마": "🍠", "버터": "🧈",
        "버섯": "🍄", "표고": "🍄", "팽이": "🍄", "양송이": "🍄",
        "호박": "🎃", "애호박": "🥒", "오이": "🥒", "가지": "🍆", "고추": "🌶️", "피망": "🫑", "파프리카": "🫑",
        "브로콜리": "🥦", "토마토": "🍅", "사과": "🍎", "배": "🍐", "바나나": "🍌", "레몬": "🍋",
        "오렌지": "🍊", "귤": "🍊", "딸기": "🍓", "포도": "🍇", "수박": "🍉", "멜론": "🍈", "키위": "🥝",
        "밤": "🌰", "땅콩": "🥜", "호두": "🥜", "아몬드": "🥜",
        "우유": "🥛", "치즈": "🧀", "요거트": "🍦", "계란": "🥚", "달걀": "🥚",
        "새우": "🍤", "게": "🦀", "꽃게": "🦀", "문어": "🐙", "낙지": "🐙", "오징어": "🦑",
        "조개": "🐚", "굴": "🦪", "전복": "🐚", "홍합": "🐚",
        "라면": "🍜", "국수": "🍜", "면": "🍝", "파스타": "🍝",
        "만두": "🥟", "떡": "🍡", "빵": "🍞", "샌드위치": "🥪",
        "햄": "🍖", "소시지": "🌭", "스팸": "🍖",
        "멸치": "🐟", "황태": "🐟", "미역": "🌿", "다시마": "🌿",
        "간장": "🍯", "고추장": "🍯", "된장": "🍯", "설탕": "🍬", "소금": "🧂", "후추": "🧂",
        "식용유": "🧴", "참기름": "🧴", "케첩": "🍅", "마요네즈": "🍼"
    }

    files = [f for f in os.listdir(base_dir) if f.lower().endswith('.png')]
    updated_count = 0
    link_count = 0
    
    print(f"Found {len(files)} renamed icon files. Syncing to DB...")

    for file_name in files:
        # 파일명에서 확장자 제거 (예: "소고기.png" -> "소고기")
        ingredient_name = os.path.splitext(file_name)[0].strip()
        
        # 1. IngredientMaster 업데이트
        # 정확히 일치하거나 포함하는 항목 찾기
        masters = IngredientMaster.objects.filter(name=ingredient_name)
        if not masters.exists():
            masters = IngredientMaster.objects.filter(name__icontains=ingredient_name)
            
        if masters.exists():
            # 매칭되는 모든 마스터 업데이트
            for master in masters:
                master.image_url = f"/media/ingredient_icons/{file_name}"
                
                # 이모지 할당
                found_emoji = None
                for key, val in emoji_dict.items():
                    if key in ingredient_name or key in master.name:
                        found_emoji = val
                        break
                
                if found_emoji:
                    master.icon = found_emoji
                
                master.save()
            updated_count += 1
            
            # 2. 실시간으로 UserIngredient와도 연결 (있으면)
            # 현재 냉장고에 있는 재료들 중 이름이 같은 것들에 master_ingredient를 연결해줌
            linked_ups = UserIngredient.objects.filter(name__icontains=ingredient_name, master_ingredient__isnull=True)
            for up in linked_ups:
                up.master_ingredient = masters.first()
                up.save()
                link_count += 1

    print(f"Successfully synced {updated_count} types of ingredients.")
    print(f"Linked {link_count} items in the actual refrigerators.")
    print("All custom icons are now applied to the database!")

if __name__ == "__main__":
    sync_renamed_icons()
