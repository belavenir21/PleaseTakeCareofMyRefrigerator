
import os
import openpyxl
import re
from django.core.management.base import BaseCommand
from master.models import IngredientMaster

class Command(BaseCommand):
    help = 'foodDB 및 ingredientDB에서 추가 식재료 데이터를 가져와 마스터 DB를 확장합니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n--- 📂 외부 DB 데이터 추가 시작 ---'))
        
        # 1. 카테고리 매핑 사전
        category_map = {
            '곡류': '곡류', '두류': '곡류', '견과': '과일/견과',
            '채소': '채소', '버섯': '채소', '과일': '과일/견과',
            '육류': '육류/달걀', '난류': '육류/달걀', '어패류': '수산/건어물', '해조류': '수산/건어물',
            '우유': '유제품', '유제품': '유제품', '음료': '음료', '차': '커피/차',
            '양념': '면/양념/오일', '조미료': '면/양념/오일', '유지류': '면/양념/오일'
        }

        # 2. ingredientDB.xlsx 처리 (약 2.5MB)
        self.import_from_ingredient_db('data/ingredientDB.xlsx', category_map)
        
        # 3. foodDB.xlsx 처리 (약 9MB, 선별적으로 추가)
        # self.import_from_food_db('data/foodDB.xlsx', category_map)

        self.stdout.write(self.style.SUCCESS('\n--- ✨ 외부 데이터 추가 완료! ---'))

    def import_from_ingredient_db(self, file_path, category_map):
        self.stdout.write(f'1. {file_path} 분석 중...')
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            count = 0
            
            # 보통 4행부터 데이터 시작 (위의 header 확인 결과)
            for row in sheet.iter_rows(min_row=4, values_only=True):
                if not row or len(row) < 4: continue
                
                raw_category = str(row[2]) if row[2] else ""
                raw_name = str(row[3]) if row[3] else ""
                
                if not raw_name or raw_name == 'None': continue
                
                # 이름 정제 (괄호 제거 등)
                name = re.sub(r'\(.*?\)', '', raw_name).split(',')[0].strip()
                if len(name) < 2: continue
                
                # 카테고리 매칭
                matched_cat = '가공식품'
                for key, val in category_map.items():
                    if key in raw_category:
                        matched_cat = val
                        break
                
                # 중복 체크 및 추가
                if not IngredientMaster.objects.filter(name=name).exists():
                    IngredientMaster.objects.create(
                        name=name,
                        category=matched_cat,
                        default_unit='개',
                        icon='📦', # 기본 이모지 (나중에 AI가 채울 수도 있음)
                        api_source='ExternalDB'
                    )
                    count += 1
                
                if count % 100 == 0 and count > 0:
                    self.stdout.write(f'   - {count}개 항목 추가됨...')
            
            self.stdout.write(self.style.SUCCESS(f'   => ingredientDB에서 {count}개 신규 항목 추가 완료'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ 에러: {str(e)}'))

    # foodDB는 너무 많고 요리 위주라 일단 보류하거나 가공식품 위주로 추가
