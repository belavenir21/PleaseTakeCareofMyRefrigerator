"""
Management command to fetch recipe data from external API (Food Safety Korea API)
"""
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Recipe, RecipeIngredient, CookingStep


class Command(BaseCommand):
    help = 'Fetch recipe data from Food Safety Korea API and populate the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit the number of recipes to fetch (default: 50)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        api_key = settings.FOODSAFETY_API_KEY
        
        if api_key == 'YOUR_API_KEY_HERE':
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  API 키가 설정되지 않았습니다. '
                    '.env 파일에 FOODSAFETY_API_KEY를 설정해주세요.'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '📝 샘플 레시피 데이터를 사용하여 데이터베이스를 초기화합니다...'
                )
            )
            self._populate_sample_recipes()
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 Food Safety Korea API에서 레시피를 가져옵니다... (최대 {limit}개)')
        )
        
        try:
            # Food Safety Korea API 호출 (정상 작동 확인됨)
            base_url = f"{settings.FOODSAFETY_API_URL}/{api_key}/COOKRCP01/json/1/{limit}"
            
            self.stdout.write(f'📡 API 호출: {base_url[:80]}...')
            
            response = requests.get(base_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # API 응답 구조 확인
                if 'COOKRCP01' in data:
                    result = data['COOKRCP01']
                    
                    # RESULT 필드로 성공/실패 확인
                    if 'RESULT' in result:
                        result_info = result['RESULT']
                        if result_info.get('CODE') == 'INFO-000':
                            self.stdout.write(
                                self.style.SUCCESS(f'✅ {result_info.get("MSG", "API 호출 성공")}')
                            )
                            self._process_api_data(data)
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'❌ API 오류: {result_info.get("MSG", "알 수 없는 오류")}'
                                )
                            )
                            self._populate_sample_recipes()
                    else:
                        # RESULT 필드가 없으면 데이터 처리
                        self._process_api_data(data)
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ 예상하지 못한 API 응답 형식')
                    )
                    self._populate_sample_recipes()
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ API 호출 실패: HTTP {response.status_code}')
                )
                self._populate_sample_recipes()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 오류 발생: {str(e)}')
            )
            self._populate_sample_recipes()

    def _process_api_data(self, data):
        """Process API response data"""
        count = 0
        
        try:
            result = data.get('COOKRCP01', {})
            items = result.get('row', [])
            
            for item in items:
                recipe_name = item.get('RCP_NM', '')  # 레시피명
                
                if recipe_name:
                    recipe, created = Recipe.objects.update_or_create(
                        api_id=item.get('RCP_SEQ', ''),
                        api_source='FoodSafetyKorea',
                        defaults={
                            'title': recipe_name,
                            'description': item.get('RCP_NA_TIP', ''),
                            'cooking_time_minutes': self._parse_time(item.get('RCP_PARTS_DTLS', '')),
                            'difficulty': '중',
                            'image_url': item.get('ATT_FILE_NO_MAIN', ''),
                            'tags': self._parse_tags(item),
                        }
                    )
                    
                    if created:
                        # 조리 단계 추가
                        self._add_cooking_steps(recipe, item)
                        count += 1
                        
            self.stdout.write(
                self.style.SUCCESS(f'✅ {count}개의 새로운 레시피가 추가되었습니다.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 데이터 처리 중 오류: {str(e)}')
            )

    def _parse_time(self, time_str):
        """Parse cooking time from string"""
        try:
            # Extract numbers from string
            import re
            numbers = re.findall(r'\d+', str(time_str))
            return int(numbers[0]) if numbers else 30
        except:
            return 30

    def _parse_tags(self, item):
        """Parse tags from recipe data"""
        tags = []
        if item.get('RCP_PAT2'):
            tags.append(item.get('RCP_PAT2'))  # 요리종류
        return tags

    def _add_cooking_steps(self, recipe, item):
        """Add cooking steps to recipe"""
        steps_data = []
        
        # Extract cooking steps from API response
        for i in range(1, 21):  # Maximum 20 steps
            manual_key = f'MANUAL{i:02d}'
            manual_text = item.get(manual_key, '').strip()
            
            if manual_text:
                steps_data.append({
                    'step_number': i,
                    'description': manual_text,
                    'time_minutes': 5,  # Default time per step
                })
        
        # Create cooking steps
        for step_data in steps_data:
            CookingStep.objects.create(
                recipe=recipe,
                **step_data
            )

    def _populate_sample_recipes(self):
        """Populate database with sample recipe data"""
        sample_recipes = [
            {
                'title': '김치찌개',
                'description': '대표적인 한국 가정식 요리로, 김치와 돼지고기를 넣어 끓인 얼큰한 찌개입니다.',
                'cooking_time': 30,
                'difficulty': '쉬움',
                'tags': ['한식', '찌개', '매운맛'],
                'ingredients': [
                    {'name': '김치', 'quantity': '200g'},
                    {'name': '돼지고기', 'quantity': '100g'},
                    {'name': '두부', 'quantity': '1/2모'},
                    {'name': '대파', 'quantity': '1/2대'},
                    {'name': '고춧가루', 'quantity': '1큰술'},
                ],
                'steps': [
                    '김치와 돼지고기를 먹기 좋은 크기로 자릅니다.',
                    '냄비에 기름을 두르고 돼지고기를 볶습니다.',
                    '김치를 넣고 함께 볶습니다.',
                    '물을 붓고 끓입니다.',
                    '두부와 대파를 넣고 한소끔 더 끓입니다.',
                    '간을 맞추고 완성합니다.',
                ]
            },
            {
                'title': '된장찌개',
                'description': '구수한 된장과 각종 채소로 끓인 건강한 찌개입니다.',
                'cooking_time': 25,
                'difficulty': '쉬움',
                'tags': ['한식', '찌개', '건강식'],
                'ingredients': [
                    {'name': '된장', 'quantity': '2큰술'},
                    {'name': '두부', 'quantity': '1/2모'},
                    {'name': '감자', 'quantity': '1개'},
                    {'name': '양파', 'quantity': '1/2개'},
                    {'name': '호박', 'quantity': '1/4개'},
                    {'name': '대파', 'quantity': '1대'},
                ],
                'steps': [
                    '감자, 양파, 호박을 먹기 좋은 크기로 자릅니다.',
                    '냄비에 물을 붓고 된장을 풀어줍니다.',
                    '감자를 먼저 넣고 끓입니다.',
                    '양파, 호박, 두부를 넣습니다.',
                    '대파를 넣고 한소끔 더 끓입니다.',
                ]
            },
            {
                'title': '불고기',
                'description': '달콤한 간장 양념에 재운 소고기를 구운 한국의 대표 요리입니다.',
                'cooking_time': 40,
                'difficulty': '중',
                'tags': ['한식', '구이', '소고기'],
                'ingredients': [
                    {'name': '소고기', 'quantity': '300g'},
                    {'name': '양파', 'quantity': '1개'},
                    {'name': '대파', 'quantity': '1대'},
                    {'name': '간장', 'quantity': '3큰술'},
                    {'name': '설탕', 'quantity': '2큰술'},
                    {'name': '마늘', 'quantity': '1큰술'},
                ],
                'steps': [
                    '소고기를 얇게 썰어 준비합니다.',
                    '간장, 설탕, 마늘 등으로 양념장을 만듭니다.',
                    '소고기에 양념을 넣고 20분간 재웁니다.',
                    '양파와 대파를 썰어 준비합니다.',
                    '팬에 재운 고기와 채소를 넣고 볶습니다.',
                    '고기가 익으면 완성입니다.',
                ]
            },
            {
                'title': '계란말이',
                'description': '부드럽고 고소한 계란으로 만든 한식 반찬입니다.',
                'cooking_time': 15,
                'difficulty': '쉬움',
                'tags': ['한식', '계란', '반찬'],
                'ingredients': [
                    {'name': '달걀', 'quantity': '3개'},
                    {'name': '대파', 'quantity': '1/4대'},
                    {'name': '당근', 'quantity': '50g'},
                    {'name': '소금', 'quantity': '약간'},
                ],
                'steps': [
                    '대파와 당근을 잘게 다집니다.',
                    '달걀을 풀고 소금으로 간합니다.',
                    '다진 대파와 당근을 넣고 섞습니다.',
                    '팬에 기름을 두르고 달궈줍니다.',
                    '계란물을 부어 돌돌 말아가며 익힙니다.',
                ]
            },
            {
                'title': '스파게티 까르보나라',
                'description': '크림 소스에 베이컨을 넣은 이탈리아 파스타 요리입니다.',
                'cooking_time': 25,
                'difficulty': '중',
                'tags': ['양식', '파스타', '크림'],
                'ingredients': [
                    {'name': '스파게티면', 'quantity': '200g'},
                    {'name': '베이컨', 'quantity': '100g'},
                    {'name': '달걀', 'quantity': '2개'},
                    {'name': '우유', 'quantity': '100ml'},
                    {'name': '파마산 치즈', 'quantity': '50g'},
                ],
                'steps': [
                    '스파게티면을 삶습니다.',
                    '베이컨을 잘게 썰어 팬에 볶습니다.',
                    '달걀과 우유, 치즈를 섞어 소스를 만듭니다.',
                    '삶은 면을 베이컨 팬에 넣습니다.',
                    '불을 끄고 소스를 부어 빠르게 섞습니다.',
                ]
            },
        ]
        
        count = 0
        for recipe_data in sample_recipes:
            recipe, created = Recipe.objects.get_or_create(
                title=recipe_data['title'],
                defaults={
                    'description': recipe_data['description'],
                    'cooking_time_minutes': recipe_data['cooking_time'],
                    'difficulty': recipe_data['difficulty'],
                    'tags': recipe_data['tags'],
                    'api_source': 'Sample',
                }
            )
            
            if created:
                # Add ingredients
                for ing_data in recipe_data['ingredients']:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        name=ing_data['name'],
                        quantity=ing_data['quantity']
                    )
                
                # Add cooking steps
                for idx, step_desc in enumerate(recipe_data['steps'], 1):
                    CookingStep.objects.create(
                        recipe=recipe,
                        step_number=idx,
                        description=step_desc,
                        time_minutes=5
                    )
                
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {count}개의 샘플 레시피가 추가되었습니다. (총 {len(sample_recipes)}개)'
            )
        )
