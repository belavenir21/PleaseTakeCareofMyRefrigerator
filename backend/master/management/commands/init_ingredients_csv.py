import csv
import os
from django.core.management.base import BaseCommand
from master.models import IngredientMaster

class Command(BaseCommand):
    help = 'Initialize ingredients from CSV file'

    def handle(self, *args, **options):
        file_path = 'data/ingredientDB2.csv'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write('🍎 Reading CSV file...')

        # 카테고리별 기본 유통기한 (일 단위)
        category_expiry_days = {
            '농축산물': 7,
            '수산물': 3,
            '가공식품': 30,
            '냉동식품': 180,
            '기타': 14
        }

        # 중복 제거를 위한 세트
        seen_names = set()
        
        # 기존 데이터 확인 (이미 있는 건 스킵하기 위해)
        existing_names = set(IngredientMaster.objects.values_list('name', flat=True))
        seen_names.update(existing_names)

        created_count = 0

        try:
            with open(file_path, 'r', encoding='cp949') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    raw_name = row.get('식품명', '').strip()
                    category = row.get('데이터구분명', '기타')
                    
                    if not raw_name:
                        continue

                    # 이름 정제 로직
                    # 1. _ 기준으로 분리하여 첫 번째 단어만 사용
                    # 2. 괄호 제거
                    clean_name = raw_name.split('_')[0]
                    clean_name = clean_name.split('(')[0].strip()

                    # 너무 짧은 이름은 스킵 (1글자) - 예: 쌀, 콩 등은 괜찮지만... 일단 포함
                    if len(clean_name) < 1:
                        continue

                    # 이미 등록된 이름이면 스킵
                    if clean_name in seen_names:
                        continue
                    
                    # 아이콘 자동 할당 (간단한 규칙)
                    icon = self.get_icon(clean_name)

                    # DB 저장
                    IngredientMaster.objects.create(
                        name=clean_name,
                        category=category,
                        default_unit='개', # 기본 단위
                        icon=icon,
                        api_source='public_data_csv'
                    )
                    
                    seen_names.add(clean_name)
                    created_count += 1
                    
                    if created_count % 100 == 0:
                        self.stdout.write(f'Processed {created_count} ingredients...')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'✅ Successfully added {created_count} new ingredients!'))

    def get_icon(self, name):
        """이름 기반으로 적절한 이모지 반환"""
        if any(x in name for x in ['사과', '배', '포도', '딸기', '바나나']): return '🍎'
        if any(x in name for x in ['고기', '돼지', '소', '닭', '햄', '베이컨']): return '🥩'
        if any(x in name for x in ['생선', '참치', '고등어', '오징어', '새우']): return '🐟'
        if any(x in name for x in ['우유', '치즈', '요거트']): return '🥛'
        if any(x in name for x in ['계란', '달걀']): return '🥚'
        if any(x in name for x in ['양파', '파', '마늘', '고추', '당근']): return '🧅'
        if any(x in name for x in ['밥', '쌀', '면', '빵', '떡']): return '🍚'
        if any(x in name for x in ['김치', '반찬']): return 'kimchi' # 이모지 없음
        return '🥘'
