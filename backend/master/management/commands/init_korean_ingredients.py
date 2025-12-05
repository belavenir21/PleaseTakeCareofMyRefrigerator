"""
Management command to populate Korean ingredient master data
한국 식재료 마스터 데이터 초기화
"""
from django.core.management.base import BaseCommand
from master.models import IngredientMaster


class Command(BaseCommand):
    help = '한국 식재료 마스터 데이터베이스 초기화'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 한국 식재료 마스터 데이터를 초기화합니다...')
        )
        
        # 한국 식재료 데이터 (카테고리별로 정리)
        korean_ingredients = [
            # 채소류
            {'name': '감자', 'category': '채소류', 'unit': 'g', 'icon': '🥔'},
            {'name': '고구마', 'category': '채소류', 'unit': 'g', 'icon': '🍠'},
            {'name': '양파', 'category': '채소류', 'unit': 'g', 'icon': '🧅'},
            {'name': '대파', 'category': '채소류', 'unit': 'g', 'icon': '🌱'},
            {'name': '쪽파', 'category': '채소류', 'unit': 'g', 'icon': '🌿'},
            {'name': '마늘', 'category': '채소류', 'unit': 'g', 'icon': '🧄'},
            {'name': '생강', 'category': '채소류', 'unit': 'g', 'icon': '🫚'},
            {'name': '당근', 'category': '채소류', 'unit': 'g', 'icon': '🥕'},
            {'name': '무', 'category': '채소류', 'unit': 'g', 'icon': '🫘'},
            {'name': '배추', 'category': '채소류', 'unit': 'g', 'icon': '🥬'},
            {'name': '양배추', 'category': '채소류', 'unit': 'g', 'icon': '🥬'},
            {'name': '브로콜리', 'category': '채소류', 'unit': 'g', 'icon': '🥦'},
            {'name': '콜리플라워', 'category': '채소류', 'unit': 'g', 'icon': '🥦'},
            {'name': '파프리카', 'category': '채소류', 'unit': 'g', 'icon': '🫑'},
            {'name': '피망', 'category': '채소류', 'unit': 'g', 'icon': '🫑'},
            {'name': '고추', 'category': '채소류', 'unit': 'g', 'icon': '🌶️'},
            {'name': '청양고추', 'category': '채소류', 'unit': 'g', 'icon': '🌶️'},
            {'name': '호박', 'category': '채소류', 'unit': 'g', 'icon': '🎃'},
            {'name': '애호박', 'category': '채소류', 'unit': 'g', 'icon': '🥒'},
            {'name': '오이', 'category': '채소류', 'unit': 'g', 'icon': '🥒'},
            {'name': '가지', 'category': '채소류', 'unit': 'g', 'icon': '🍆'},
            {'name': '토마토', 'category': '채소류', 'unit': 'g', 'icon': '🍅'},
            {'name': '방울토마토', 'category': '채소류', 'unit': 'g', 'icon': '🍅'},
            {'name': '상추', 'category': '채소류', 'unit': 'g', 'icon': '🥬'},
            {'name': '깻잎', 'category': '채소류', 'unit': '장', 'icon': '🍃'},
            {'name': '시금치', 'category': '채소류', 'unit': 'g', 'icon': '🥬'},
            {'name': '미나리', 'category': '채소류', 'unit': 'g', 'icon': '🌿'},
            {'name': '쑥갓', 'category': '채소류', 'unit': 'g', 'icon': '🌿'},
            {'name': '부추', 'category': '채소류', 'unit': 'g', 'icon': '🌱'},
            {'name': '콩나물', 'category': '채소류', 'unit': 'g', 'icon': '🌱'},
            {'name': '숙주나물', 'category': '채소류', 'unit': 'g', 'icon': '🌱'},
            
            # 버섯류
            {'name': '느타리버섯', 'category': '버섯류', 'unit': 'g', 'icon': '🍄'},
            {'name': '팽이버섯', 'category': '버섯류', 'unit': 'g', 'icon': '🍄'},
            {'name': '새송이버섯', 'category': '버섯류', 'unit': 'g', 'icon': '🍄'},
            {'name': '표고버섯', 'category': '버섯류', 'unit': 'g', 'icon': '🍄'},
            {'name': '양송이버섯', 'category': '버섯류', 'unit': 'g', 'icon': '🍄'},
            
            # 육류
            {'name': '소고기', 'category': '육류', 'unit': 'g', 'icon': '🥩'},
            {'name': '돼지고기', 'category': '육류', 'unit': 'g', 'icon': '🥓'},
            {'name': '닭고기', 'category': '육류', 'unit': 'g', 'icon': '🍗'},
            {'name': '삼겹살', 'category': '육류', 'unit': 'g', 'icon': '🥓'},
            {'name': '목살', 'category': '육류', 'unit': 'g', 'icon': '🥓'},
            {'name': '등심', 'category': '육류', 'unit': 'g', 'icon': '🥩'},
            {'name': '안심', 'category': '육류', 'unit': 'g', 'icon': '🥩'},
            {'name': '닭가슴살', 'category': '육류', 'unit': 'g', 'icon': '🍗'},
            {'name': '닭다리', 'category': '육류', 'unit': 'g', 'icon': '🍗'},
            {'name': '베이컨', 'category': '육류', 'unit': 'g', 'icon': '🥓'},
            {'name': '소시지', 'category': '육류', 'unit': '개', 'icon': '🌭'},
            {'name': '햄', 'category': '육류', 'unit': 'g', 'icon': '🍖'},
            
            # 해산물
            {'name': '고등어', 'category': '해산물', 'unit': '마리', 'icon': '🐟'},
            {'name': '갈치', 'category': '해산물', 'unit': '마리', 'icon': '🐟'},
            {'name': '조기', 'category': '해산물', 'unit': '마리', 'icon': '🐟'},
            {'name': '삼치', 'category': '해산물', 'unit': '마리', 'icon': '🐟'},
            {'name': '연어', 'category': '해산물', 'unit': 'g', 'icon': '🐠'},
            {'name': '참치', 'category': '해산물', 'unit': 'g', 'icon': '🐟'},
            {'name': '새우', 'category': '해산물', 'unit': 'g', 'icon': '🦐'},
            {'name': '오징어', 'category': '해산물', 'unit': '마리', 'icon': '🦑'},
            {'name': '낙지', 'category': '해산물', 'unit': '마리', 'icon': '🐙'},
            {'name': '문어', 'category': '해산물', 'unit': 'g', 'icon': '🐙'},
            {'name': '조개', 'category': '해산물', 'unit': 'g', 'icon': '🦪'},
            {'name': '바지락', 'category': '해산물', 'unit': 'g', 'icon': '🦪'},
            {'name': '홍합', 'category': '해산물', 'unit': 'g', 'icon': '🦪'},
            {'name': '굴', 'category': '해산물', 'unit': 'g', 'icon': '🦪'},
            {'name': '게', 'category': '해산물', 'unit': '마리', 'icon': '🦀'},
            {'name': '명란', 'category': '해산물', 'unit': 'g', 'icon': '🥚'},
            
            # 유제품
            {'name': '우유', 'category': '유제품', 'unit': 'ml', 'icon': '🥛'},
            {'name': '두유', 'category': '유제품', 'unit': 'ml', 'icon': '🥛'},
            {'name': '치즈', 'category': '유제품', 'unit': 'g', 'icon': '🧀'},
            {'name': '모짜렐라치즈', 'category': '유제품', 'unit': 'g', 'icon': '🧀'},
            {'name': '체다치즈', 'category': '유제품', 'unit': 'g', 'icon': '🧀'},
            {'name': '요거트', 'category': '유제품', 'unit': 'g', 'icon': '🥛'},
            {'name': '생크림', 'category': '유제품', 'unit': 'ml', 'icon': '🥛'},
            {'name': '버터', 'category': '유제품', 'unit': 'g', 'icon': '🧈'},
            
            # 과일류
            {'name': '사과', 'category': '과일류', 'unit': '개', 'icon': '🍎'},
            {'name': '배', 'category': '과일류', 'unit': '개', 'icon': '🍐'},
            {'name': '바나나', 'category': '과일류', 'unit': '개', 'icon': '🍌'},
            {'name': '딸기', 'category': '과일류', 'unit': 'g', 'icon': '🍓'},
            {'name': '포도', 'category': '과일류', 'unit': 'g', 'icon': '🍇'},
            {'name': '수박', 'category': '과일류', 'unit': 'g', 'icon': '🍉'},
            {'name': '참외', 'category': '과일류', 'unit': '개', 'icon': '🍈'},
            {'name': '멜론', 'category': '과일류', 'unit': '개', 'icon': '🍈'},
            {'name': '귤', 'category': '과일류', 'unit': '개', 'icon': '🍊'},
            {'name': '오렌지', 'category': '과일류', 'unit': '개', 'icon': '🍊'},
            {'name': '레몬', 'category': '과일류', 'unit': '개', 'icon': '🍋'},
            {'name': '자두', 'category': '과일류', 'unit': '개', 'icon': '🍑'},
            {'name': '복숭아', 'category': '과일류', 'unit': '개', 'icon': '🍑'},
            {'name': '키위', 'category': '과일류', 'unit': '개', 'icon': '🥝'},
            {'name': '망고', 'category': '과일류', 'unit': '개', 'icon': '🥭'},
            {'name': '파인애플', 'category': '과일류', 'unit': '개', 'icon': '🍍'},
            {'name': '블루베리', 'category': '과일류', 'unit': 'g', 'icon': '🫐'},
            
            # 곡물/면류
            {'name': '쌀', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '현미', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '찹쌀', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '밀가루', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '부침가루', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '빵가루', 'category': '곡물류', 'unit': 'g', 'icon': '🍞'},
            {'name': '식빵', 'category': '곡물류', 'unit': '장', 'icon': '🍞'},
            {'name': '라면', 'category': '면류', 'unit': '개', 'icon': '🍜'},
            {'name': '우동면', 'category': '면류', 'unit': 'g', 'icon': '🍜'},
            {'name': '소면', 'category': '면류', 'unit': 'g', 'icon': '🍜'},
            {'name': '당면', 'category': '면류', 'unit': 'g', 'icon': '🍜'},
            {'name': '스파게티면', 'category': '면류', 'unit': 'g', 'icon': '🍝'},
            
            # 난류
            {'name': '달걀', 'category': '난류', 'unit': '개', 'icon': '🥚'},
            {'name': '메추리알', 'category': '난류', 'unit': '개', 'icon': '🥚'},
            
            # 두부/콩류
            {'name': '두부', 'category': '두부/콩류', 'unit': 'g', 'icon': '🧈'},
            {'name': '순두부', 'category': '두부/콩류', 'unit': 'g', 'icon': '🧈'},
            {'name': '콩', 'category': '두부/콩류', 'unit': 'g', 'icon': '🫘'},
            {'name': '밤', 'category': '견과류', 'unit': '개', 'icon': '🌰'},
            {'name': '땅콩', 'category': '견과류', 'unit': 'g', 'icon': '🥜'},
            {'name': '아몬드', 'category': '견과류', 'unit': 'g', 'icon': '🌰'},
            {'name': '호두', 'category': '견과류', 'unit': 'g', 'icon': '🌰'},
            
            # 조미료/양념
            {'name': '소금', 'category': '조미료', 'unit': 'g', 'icon': '🧂'},
            {'name': '설탕', 'category': '조미료', 'unit': 'g', 'icon': '🍬'},
            {'name': '간장', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '된장', 'category': '조미료', 'unit': 'g', 'icon': '🥫'},
            {'name': '고추장', 'category': '조미료', 'unit': 'g', 'icon': '🌶️'},
            {'name': '쌈장', 'category': '조미료', 'unit': 'g', 'icon': '🥫'},
            {'name': '참기름', 'category': '조미료', 'unit': 'ml', 'icon': '🛢️'},
            {'name': '들기름', 'category': '조미료', 'unit': 'ml', 'icon': '🛢️'},
            {'name': '식용유', 'category': '조미료', 'unit': 'ml', 'icon': '🛢️'},
            {'name': '올리브유', 'category': '조미료', 'unit': 'ml', 'icon': '🛢️'},
            {'name': '참깨', 'category': '조미료', 'unit': 'g', 'icon': '🌾'},
            {'name': '깨소금', 'category': '조미료', 'unit': 'g', 'icon': '🌾'},
            {'name': '고춧가루', 'category': '조미료', 'unit': 'g', 'icon': '🌶️'},
            {'name': '후추', 'category': '조미료', 'unit': 'g', 'icon': '⚫'},
            {'name': '식초', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '물엿', 'category': '조미료', 'unit': 'g', 'icon': '🍯'},
            {'name': '꿀', 'category': '조미료', 'unit': 'g', 'icon': '🍯'},
            {'name': '미림', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '맛술', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '굴소스', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '케첩', 'category': '조미료', 'unit': 'g', 'icon': '🍅'},
            {'name': '마요네즈', 'category': '조미료', 'unit': 'g', 'icon': '🥫'},
            {'name': '머스타드', 'category': '조미료', 'unit': 'g', 'icon': '🥫'},
        ]
        
        count = 0
        for item in korean_ingredients:
            obj, created = IngredientMaster.objects.update_or_create(
                name=item['name'],
                defaults={
                    'category': item['category'],
                    'default_unit': item['unit'],
                    'icon': item['icon'],
                    'api_source': 'Korean_Master',
                }
            )
            if created:
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {count}개의 새로운 식재료가 추가되었습니다. '
                f'(총 {len(korean_ingredients)}개)'
            )
        )
        
        # 카테고리별 통계
        from collections import Counter
        categories = Counter([item['category'] for item in korean_ingredients])
        
        self.stdout.write(self.style.SUCCESS('\n📊 카테고리별 통계:'))
        for category, cnt in sorted(categories.items()):
            self.stdout.write(f'  - {category}: {cnt}개')
