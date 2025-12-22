import os
import django
import json
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def rename_and_update_all_in_one():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    
    # 162개 전체 명단 (이미지 순서대로)
    name_list = [
        "소고기", "삼겹살", "생닭", "생선", "두부", "청경채", "배추", "깻잎", "시금치", "부추", "얼갈이배추", "비타민", "공심채", "미나리", "쑥갓", "고구마순", "자색고구마",
        "무", "당근", "양파", "마늘", "감자", "고구마", "양송이버섯", "팽이버섯", "새송이버섯", "애호박", "오이", "가지", "고추", "피망", "숙주", "브로콜리", "양배추",
        "방울토마토", "단호박", "대파", "생강", "레몬", "사과", "서양배", "바나나", "오렌지", "귤", "체리", "도토리", "밤", "대추", "땅콩", "호두", "피칸",
        "아몬드", "베이컨", "참치캔", "만두", "천등", "거봉", "딸기", "포도", "수박", "멜론", "키위", "군밤", "대추야자", "생땅콩", "호두알", "껍질호두", "피넛",
        "슬라이스아몬드", "통아몬드", "캐슈넛", "들깨", "흑임자", "참깨", "검은콩", "말린나물", "은행", "연근", "우엉", "도라지", "더덕", "인삼", "고사리", "말린미역", "다시마",
        "건다시마", "파래", "상추", "전", "연어", "단무지", "샐러드무", "간장", "된장", "고추장", "쌈장", "명란젓", "액젓", "미림", "가쓰오부시", "올리브유", "식용유",
        "참기름", "설탕", "소금", "후추", "고춧가루", "케첩", "머스타드", "고추장봉지", "카레가루", "밀가루", "전분가루", "튀김가루", "부침가루", "빵가루", "소면", "당면", "파스타면",
        "라면", "컵라면", "떡볶이떡", "만두피", "비엔나소시지", "스팸", "베이컨줄", "참치캔2", "런천미트", "치즈", "버터", "우유", "요거트", "플레인요거트", "메추리알", "계란후라이", "계란",
        "오리알", "꽃게", "새우", "꼴뚜기", "문어", "조개", "홍합", "굴", "가리비", "전복", "꼬막", "멍게", "해삼", "미더덕", "말린새우", "맛살", "멸치",
        "뱅어포", "황태", "오징어채", "육포", "해파리", "문어다리", "게살", "연어알", "조개관자"
    ]

    # 이모지 매칭 사전 (간단 버전, 필요시 확장 가능)
    emoji_dict = {
        "소고기": "🥩", "삼겹살": "🥓", "닭": "🍗", "생선": "🐟", "두부": "⬜", "채소": "🥬", "배추": "🥬",
        "무": "🍖", "당근": "🥕", "양파": "🧅", "마늘": "🧄", "감자": "🥔", "고구마": "🍠", "버섯": "🍄",
        "호박": "🎃", "오이": "🥒", "가지": "🍆", "고추": "🌶️", "피망": "🫑", "브로콜리": "🥦", "사과": "🍎",
        "바나나": "🍌", "레몬": "🍋", "오렌지": "🍊", "귤": "🍊", "딸기": "🍓", "포도": "🍇", "수박": "🍉",
        "멜론": "🍈", "키위": "🥝", "밤": "🌰", "땅콩": "🥜", "우유": "🥛", "치즈": "🧀", "계란": "🥚",
        "새우": "🍤", "게": "🦀", "문어": "🐙", "라면": "🍜", "만두": "🥟", "식빵": "🍞", "버터": "🧈"
    }

    files = sorted([f for f in os.listdir(base_dir) if f.startswith('icon_')])
    mapping_log = []
    
    print(f"Starting to rename and update {len(files)} icons...")

    for i, file_name in enumerate(files):
        if i >= len(name_list): break
            
        old_path = os.path.join(base_dir, file_name)
        new_name = name_list[i].strip()
        new_file_name = f"{new_name}.png"
        new_path = os.path.join(base_dir, new_file_name)
        
        try:
            # 1. 파일 이름 변경
            if os.path.exists(new_path) and old_path != new_path:
                new_file_name = f"{new_name}_{i}.png"
                new_path = os.path.join(base_dir, new_file_name)
            os.rename(old_path, new_path)
            
            # 2. DB 매칭 및 이모지 할당
            master = IngredientMaster.objects.filter(name=new_name).first()
            if not master:
                master = IngredientMaster.objects.filter(name__icontains=new_name).first()
            
            if master:
                # 이미지 URL 업데이트
                master.image_url = f"/media/ingredient_icons/{new_file_name}"
                
                # 어울리는 이모지 찾기
                found_emoji = None
                for key, val in emoji_dict.items():
                    if key in new_name:
                        found_emoji = val
                        break
                
                if found_emoji:
                    master.icon = found_emoji
                
                master.save()
                mapping_log.append(f"SUCCESS: {new_file_name} -> DB({master.name}) / Emoji({master.icon})")
            else:
                mapping_log.append(f"RENAME ONLY: {new_file_name} (No DB match)")
                
        except Exception as e:
            mapping_log.append(f"ERROR {new_name}: {str(e)}")

    with open('final_icon_update_log.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(mapping_log))
    
    print(f"Finished! Check final_icon_update_log.txt for details.")

if __name__ == "__main__":
    rename_and_update_all_in_one()
