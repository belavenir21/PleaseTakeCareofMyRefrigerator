import os
import django
import json
import re

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def rename_and_update_db(name_list=None):
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    
    # 이미 파일 이름이 바뀌었으므로, 폴더 내의 모든 png 파일을 대상으로 매칭
    files = [f for f in os.listdir(base_dir) if f.endswith('.png')]
    
    synonyms = {
        "삼겹살": "돼지고기", "생닭": "닭고기", "생선": "조개",
        "무": "무순", "새송이버섯": "느타리버섯", "애호박": "호박",
        "방울토마토": "토마토", "단호박": "호박", "서양배": "배",
        "참치캔": "참치", "참치캔2": "참치", "거봉": "포도",
        "계란": "달걀", "계란후라이": "달걀", "꽃게": "게",
        "스팸": "햄", "런천미트": "햄", "비엔나소시지": "소시지",
        "베이컨줄": "베이컨", "맛살": "게맛살", "육포": "소고기"
    }

    mapping_log = []
    
    for file_name in files:
        # 파일명에서 확장자 제거하여 원래 재료명 추출 (예: "소고기.png" -> "소고기")
        orig_name = os.path.splitext(file_name)[0]
        # 번호가 붙은 경우 제거 (예: "소고기_123" -> "소고기")
        search_base = re.sub(r'_\d+$', '', orig_name)
        
        try:
            # DB 매칭 로직
            search_names = [search_base]
            if search_base in synonyms:
                search_names.append(synonyms[search_base])
            
            master = None
            for s_name in search_names:
                master = IngredientMaster.objects.filter(name=s_name).first()
                if master: break
                master = IngredientMaster.objects.filter(name__icontains=s_name).first()
                if master: break
            
            if master:
                master.image_url = f"/media/ingredient_icons/{file_name}"
                master.save()
                mapping_log.append(f"Linked: {file_name} -> {master.name}")
            else:
                mapping_log.append(f"No DB Match: {file_name}")
                
        except Exception as e:
            mapping_log.append(f"Error {file_name}: {str(e)}")

    with open('icon_mapping_log.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(mapping_log))
    print(f"Finished processing {len(mapping_log)} files.")

if __name__ == "__main__":
    # 156개 아이콘 이름 리스트 (가로 방향 우선 순서)
    names = [
        # Row 1
        "소고기", "삼겹살", "생닭", "생선", "두부", "청경채", "배추", "깻잎", "시금치", "부추", 
        "얼갈이배추", "비타민", "공심채", "미나리", "쑥갓", "고구마순", "자색고구마",
        # Row 2
        "무", "당근", "양파", "마늘", "감자", "고구마", "양송이버섯", "팽이버섯", "새송이버섯", 
        "애호박", "오이", "가지", "고추", "피망", "숙주", "브로콜리", "양배추",
        # Row 3
        "방울토마토", "단호박", "대파", "생강", "레몬", "사과", "서양배", "바나나", "귤", 
        "체리", "도토리", "밤", "대추", "땅콩", "호두", "피칸", "아몬드", "베이컨", "참치캔", "만두",
        # Row 4
        "오렌지", "거봉", "딸기", "포도", "수박", "멜론", "키위", "군밤", "대추야자", "생땅콩",
        "호두알", "껍질호두", "피넛", "슬라이스아몬드", "통아몬드", "캐슈넛", "들깨", "흑임자",
        # Row 5
        "참깨", "검은콩", "말린나물", "은행", "연근", "우엉", "도라지", "더덕", "인삼", "고사리",
        "말린미역", "다시마", "건다시마", "파래", "상추", "전", "연어", "단무지",
        # Row 6
        "샐러드무", "간장", "된장", "고추장", "쌈장", "명란젓", "액젓", "미림", "가쓰오부시", "올리브유",
        "식용유", "참기름", "설탕", "소금", "후추", "고춧가루", "케첩", "머스타드",
        # Row 7
        "고추장봉지", "카레가루", "밀가루", "전분가루", "튀김가루", "부침가루", "빵가루", "소면", "당면", "파스타면",
        "라면", "컵라면", "떡볶이떡", "만두피", "비엔나소시지", "스팸", "베이컨줄",
        # Row 8
        "참치캔2", "런천미트", "치즈", "버터", "우유", "요거트", "플레인요거트", "메추리알", "계란후라이", "계란",
        "오리알", "꽃게", "새우", "꼴뚜기", "문어", "조개", "홍합", "굴",
        # Row 9
        "가리비", "전복", "꼬막", "멍게", "해삼", "미더덕", "말린새우", "맛살", "멸치", "뱅어포", "황태", "오징어채", "육포"
    ]
    
    # 부족한 개수 채우기 (안전장치)
    while len(names) < 156:
        names.append(f"미분류_{len(names)}")
        
    rename_and_update_db(names)

