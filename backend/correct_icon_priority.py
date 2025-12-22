import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def correct_icon_priority():
    """
    올바른 우선순위:
    1. 완벽한 이모지가 있으면 이모지 우선 (커스텀 이미지 무시)
    2. 이모지가 없거나 부정확하면 커스텀 이미지 사용
    3. 특수 케이스 처리
    """
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    files = {os.path.splitext(f)[0]: f for f in os.listdir(base_dir) if f.lower().endswith('.png')}
    
    # 완벽한 이모지 매핑 (이것들은 커스텀 이미지보다 우선)
    PERFECT_EMOJIS = {
        # 과일
        "사과": "🍎", "레몬": "🍋", "오렌지": "🍊", "귤": "🍊", 
        "바나나": "🍌", "딸기": "🍓", "포도": "🍇", "청포도": "🍇",
        "수박": "🍉", "멜론": "🍈", "키위": "🥝", 
        "복숭아": "🍑", "체리": "🍒", "망고": "🥭", "파인애플": "🍍",
        "코코넛": "🥥", "아보카도": "🥑",
        
        # 채소 (이모지가 명확한 것만)
        "당근": "🥕", "감자": "🥔", "고구마": "🍠", 
        "옥수수": "🌽", "토마토": "🍅", "오이": "🥒", 
        "가지": "🍆", "버섯": "🍄", "브로콜리": "🥦",
        "고추": "🌶️", "피망": "🫑", "마늘": "🧄", "양파": "🧅",
        
        # 유제품
        "우유": "🥛", "치즈": "🧀", "버터": "🧈",
        
        # 알
        "계란": "🥚", "달걀": "🥚",
        
        # 기타
        "소금": "🧂", "빵": "🍞", "쌀": "🍚",
        "꿀": "🍯", "설탕": "🍬"
    }
    
    # 특수 케이스: 수동 매핑
    SPECIAL_CASES = {
        "숙주": {"image_url": "/media/ingredient_icons/콩나물.png", "icon": "🌱"},
        "숙주나물": {"image_url": "/media/ingredient_icons/콩나물.png", "icon": "🌱"}
    }
    
    all_masters = IngredientMaster.objects.all()
    count_emoji_only = 0
    count_image = 0
    count_default = 0
    
    for master in all_masters:
        # 특수 케이스 먼저 처리
        if master.name in SPECIAL_CASES:
            special = SPECIAL_CASES[master.name]
            master.image_url = special["image_url"]
            master.icon = special["icon"]
            master.save()
            count_image += 1
            continue
        
        # 1단계: 완벽한 이모지가 있으면 이모지만 사용 (이미지 무시)
        if master.name in PERFECT_EMOJIS:
            master.icon = PERFECT_EMOJIS[master.name]
            master.image_url = None  # 이모지 우선이므로 이미지 제거
            count_emoji_only += 1
        
        # 2단계: 이모지가 없으면 커스텀 이미지 찾기
        else:
            # 정확히 일치하는 파일
            if master.name in files:
                master.image_url = f"/media/ingredient_icons/{files[master.name]}"
                master.icon = "📦"  # 보조 아이콘
                count_image += 1
            else:
                # 부분 일치 파일
                matching_file = None
                for fname in files.keys():
                    if len(fname) > 1 and (fname in master.name or master.name in fname):
                        matching_file = files[fname]
                        break
                
                if matching_file:
                    master.image_url = f"/media/ingredient_icons/{matching_file}"
                    master.icon = "📦"
                    count_image += 1
                else:
                    # 둘 다 없으면 기본
                    master.icon = "📦"
                    master.image_url = None
                    count_default += 1
        
        master.save()
    
    print("\n=== 올바른 우선순위 적용 완료 ===")
    print(f"[완벽한 이모지 우선]: {count_emoji_only}개")
    print(f"  예: 양파 -> 양파 이모지, 사과 -> 사과 이모지")
    print(f"[커스텀 이미지 사용]: {count_image}개")
    print(f"  예: 대파 -> 대파.png, 숙주 -> 콩나물.png")
    print(f"[기본 아이콘]: {count_default}개")

if __name__ == "__main__":
    correct_icon_priority()
