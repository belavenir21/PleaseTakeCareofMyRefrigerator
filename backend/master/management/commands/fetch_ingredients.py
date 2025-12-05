"""
Management command to fetch ingredient data from external API (AgriFood API)
"""
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from master.models import IngredientMaster


class Command(BaseCommand):
    help = 'Fetch ingredient data from AgriFood API and populate the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limit the number of ingredients to fetch (default: 100)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        api_key = settings.AGRIFOOD_API_KEY
        
        if api_key == 'YOUR_API_KEY_HERE':
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  API 키가 설정되지 않았습니다. '
                    '.env 파일에 AGRIFOOD_API_KEY를 설정해주세요.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '📝 샘플 데이터를 사용하여 데이터베이스를 초기화합니다...'
                )
            )
            self._populate_sample_data()
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 AgriFood API에서 재료 데이터를 가져옵니다... (최대 {limit}개)')
        )
        
        try:
            # AgriFood API 호출
            base_url = settings.AGRIFOOD_API_URL
            params = {
                'serviceKey': api_key,
                'numOfRows': limit,
                'pageNo': 1,
                'type': 'json'
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self._process_api_data(data)
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ API 호출 실패: {response.status_code}'
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS('📝 샘플 데이터를 사용합니다...')
                )
                self._populate_sample_data()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 오류 발생: {str(e)}')
            )
            self.stdout.write(
                self.style.SUCCESS('📝 샘플 데이터를 사용합니다...')
            )
            self._populate_sample_data()

    def _process_api_data(self, data):
        """Process API response data"""
        count = 0
        
        try:
            items = data.get('items', [])
            
            for item in items:
                ingredient_name = item.get('fdnm', '')  # 식품명
                category = item.get('fdtyCdNm', '기타')  # 식품 대분류명
                image_url = item.get('imgUrl1', '')  # 이미지 URL
                
                if ingredient_name:
                    obj, created = IngredientMaster.objects.update_or_create(
                        name=ingredient_name,
                        defaults={
                            'category': category,
                            'default_unit': 'g',
                            'image_url': image_url,
                            'api_source': 'AgriFood',
                            'api_id': item.get('fdCd', ''),
                        }
                    )
                    
                    if created:
                        count += 1
                        
            self.stdout.write(
                self.style.SUCCESS(f'✅ {count}개의 새로운 재료가 추가되었습니다.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 데이터 처리 중 오류: {str(e)}')
            )

    def _populate_sample_data(self):
        """Populate database with sample ingredient data"""
        sample_ingredients = [
            # 채소류
            {'name': '감자', 'category': '채소류', 'unit': 'g', 'icon': '🥔'},
            {'name': '양파', 'category': '채소류', 'unit': 'g', 'icon': '🧅'},
            {'name': '당근', 'category': '채소류', 'unit': 'g', 'icon': '🥕'},
            {'name': '브로콜리', 'category': '채소류', 'unit': 'g', 'icon': '🥦'},
            {'name': '배추', 'category': '채소류', 'unit': 'g', 'icon': '🥬'},
            {'name': '무', 'category': '채소류', 'unit': 'g', 'icon': '🫘'},
            {'name': '대파', 'category': '채소류', 'unit': 'g', 'icon': '🌱'},
            {'name': '마늘', 'category': '채소류', 'unit': 'g', 'icon': '🧄'},
            {'name': '고추', 'category': '채소류', 'unit': 'g', 'icon': '🌶️'},
            {'name': '파프리카', 'category': '채소류', 'unit': 'g', 'icon': '🫑'},
            
            # 육류
            {'name': '소고기', 'category': '육류', 'unit': 'g', 'icon': '🥩'},
            {'name': '돼지고기', 'category': '육류', 'unit': 'g', 'icon': '🥓'},
            {'name': '닭고기', 'category': '육류', 'unit': 'g', 'icon': '🍗'},
            
            # 해산물
            {'name': '고등어', 'category': '해산물', 'unit': 'g', 'icon': '🐟'},
            {'name': '연어', 'category': '해산물', 'unit': 'g', 'icon': '🐠'},
            {'name': '새우', 'category': '해산물', 'unit': 'g', 'icon': '🦐'},
            {'name': '오징어', 'category': '해산물', 'unit': 'g', 'icon': '🦑'},
            
            # 유제품
            {'name': '우유', 'category': '유제품', 'unit': 'ml', 'icon': '🥛'},
            {'name': '치즈', 'category': '유제품', 'unit': 'g', 'icon': '🧀'},
            {'name': '요거트', 'category': '유제품', 'unit': 'g', 'icon': '🥛'},
            {'name': '버터', 'category': '유제품', 'unit': 'g', 'icon': '🧈'},
            
            # 과일류
            {'name': '사과', 'category': '과일류', 'unit': '개', 'icon': '🍎'},
            {'name': '바나나', 'category': '과일류', 'unit': '개', 'icon': '🍌'},
            {'name': '딸기', 'category': '과일류', 'unit': 'g', 'icon': '🍓'},
            {'name': '포도', 'category': '과일류', 'unit': 'g', 'icon': '🍇'},
            {'name': '수박', 'category': '과일류', 'unit': 'g', 'icon': '🍉'},
            
            # 곡물/면류
            {'name': '쌀', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '밀가루', 'category': '곡물류', 'unit': 'g', 'icon': '🌾'},
            {'name': '라면', 'category': '면류', 'unit': '개', 'icon': '🍜'},
            {'name': '스파게티면', 'category': '면류', 'unit': 'g', 'icon': '🍝'},
            
            # 달걀
            {'name': '달걀', 'category': '난류', 'unit': '개', 'icon': '🥚'},
            
            # 조미료
            {'name': '소금', 'category': '조미료', 'unit': 'g', 'icon': '🧂'},
            {'name': '설탕', 'category': '조미료', 'unit': 'g', 'icon': '🍬'},
            {'name': '간장', 'category': '조미료', 'unit': 'ml', 'icon': '🍶'},
            {'name': '고추장', 'category': '조미료', 'unit': 'g', 'icon': '🌶️'},
            {'name': '된장', 'category': '조미료', 'unit': 'g', 'icon': '🥫'},
            {'name': '식용유', 'category': '조미료', 'unit': 'ml', 'icon': '🛢️'},
        ]
        
        count = 0
        for item in sample_ingredients:
            obj, created = IngredientMaster.objects.update_or_create(
                name=item['name'],
                defaults={
                    'category': item['category'],
                    'default_unit': item['unit'],
                    'icon': item['icon'],
                    'api_source': 'Sample',
                }
            )
            if created:
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {count}개의 샘플 재료가 추가되었습니다. (총 {len(sample_ingredients)}개)'
            )
        )
