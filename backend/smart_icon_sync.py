import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def smart_icon_assignment():
    """
    사용자 요청에 따른 지능형 아이콘 배정:
    1. 정확히 일치하는 커스텀 이미지가 있으면 우선 사용 (예: 대파.png)
    2. 없으면, 기본 단어가 포함되어 있을 때 이모지 사용 (예: 레몬그라스 → 🍋)
    3. 둘 다 없으면 부분 일치하는 커스텀 이미지 찾기
    4. 그것도 없으면 기본 이모지
    """
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    files = {os.path.splitext(f)[0]: f for f in os.listdir(base_dir) if f.lower().endswith('.png')}
    
    # 기본 단어 이모지 매핑 (포함 관계로 확장)
    BASE_EMOJIS = {
        "레몬": "🍋", "오렌지": "🍊", "귤": "🍊", "사과": "🍎", "배": "🍐", 
        "바나나": "🍌", "딸기": "🍓", "포도": "🍇", "수박": "🍉", "멜론": "🍈",
        "키위": "🥝", "복숭아": "🍑", "체리": "🍒", "망고": "🥭", "파인애플": "🍍",
        "당근": "🥕", "감자": "🥔", "고구마": "🍠", "마늘": "🧄",
        "옥수수": "🌽", "토마토": "🍅", "오이": "🥒", "가지": "🍆",
        "버섯": "🍄", "브로콜리": "🥦", "양배추": "🥬",
        "고추": "🌶️", "피망": "🫑",
        "우유": "🥛", "치즈": "🧀", "버터": "🧈", "요거트": "🍦",
        "계란": "🥚", "달걀": "🥚",
        "소금": "🧂", "후추": "🧂", "설탕": "🍬",
        "빵": "🍞", "도넛": "🍩", "쿠키": "🍪",
        "커피": "☕", "차": "🍵",
        "물": "💧", "쌀": "🍚",
        "꿀": "🍯"
    }
    
    # 예외 처리: 정확한 파일이 있으면 이모지보다 우선 (대파, 소고기 등 세부 구분)
    EXACT_FILE_PRIORITY = [
        "대파", "쪽파", "소고기", "돼지고기", "닭고기", "양고기",
        "새우", "게", "꽃게", "문어", "오징어", "낙지",
        "배추", "양배추", "청경채", "상추"
    ]
    
    all_masters = IngredientMaster.objects.all()
    count_emoji = 0
    count_image = 0
    count_default = 0
    
    for master in all_masters:
        # 1단계: 정확히 일치하는 커스텀 이미지 우선 (예외 우선순위)
        if master.name in files:
            master.image_url = f"/media/ingredient_icons/{files[master.name]}"
            # 기본 이모지는 보조용으로
            for key, emoji in BASE_EMOJIS.items():
                if key in master.name:
                    master.icon = emoji
                    break
            if not master.icon:
                master.icon = "📦"
            count_image += 1
        
        # 2단계: 기본 단어가 포함되어 있으면 이모지 우선 (레몬그라스 → 🍋)
        else:
            found_emoji = None
            for key, emoji in BASE_EMOJIS.items():
                if key in master.name:
                    found_emoji = emoji
                    break
            
            if found_emoji:
                master.icon = found_emoji
                master.image_url = None  # 이모지 우선
                count_emoji += 1
            else:
                # 3단계: 부분 일치하는 커스텀 이미지 찾기
                matching_file = None
                for fname in files.keys():
                    if fname in master.name or master.name in fname:
                        if len(fname) > 1:  # 너무 짧은 매칭은 제외
                            matching_file = files[fname]
                            break
                
                if matching_file:
                    master.image_url = f"/media/ingredient_icons/{matching_file}"
                    master.icon = "📦"
                    count_image += 1
                else:
                    # 4단계: 둘 다 없으면 기본값
                    master.icon = "📦"
                    master.image_url = None
                    count_default += 1
        
        master.save()
    
    print("\n=== 지능형 아이콘 배정 완료 ===")
    print(f"[이모지 우선] 기본 단어 포함: {count_emoji}개")
    print(f"[커스텀 이미지 우선]: {count_image}개")
    print(f"[기본 아이콘만]: {count_default}개")
    print("\n예시:")
    print("  - 레몬그라스 -> 레몬 이모지 (레몬 포함)")
    print("  - 대파 -> 대파.png (정확한 이미지 존재)")
    print("  - 양파 -> 양파 이모지 (기본 이모지)")

if __name__ == "__main__":
    smart_icon_assignment()
