"""
노이즈 데이터 정리 커맨드
OCR 테스트 중 생성된 잘못된 데이터를 DB에서 삭제
"""
from django.core.management.base import BaseCommand
from master.models import IngredientMaster
import re


class Command(BaseCommand):
    help = 'OCR 노이즈 데이터 정리 (브랜드명, 숫자 혼합, 의미없는 텍스트 등)'

    def handle(self, *args, **options):
        self.stdout.write('[노이즈 데이터 검색 중...]\n')
        
        # 노이즈 패턴 정의
        noise_patterns = [
            # 1. 브랜드명이 포함된 것들
            (r'노브랜드', '브랜드명 포함'),
            (r'농심', '브랜드명 포함'),
            (r'오뚜기|오두기', '브랜드명 포함'),
            (r'청정원', '브랜드명 포함'),
            (r'CJ|씨제이', '브랜드명 포함'),
            (r'풀무원', '브랜드명 포함'),
            
            # 2. 숫자가 많이 섞인 것들
            (r'.*\d{3,}.*', '숫자 과다'),
            
            # 3. 영문+숫자 조합 (상품코드 같은 것)
            (r'.*[A-Z]{1,3}\s*\d+.*', '상품코드'),
            
            # 4. 특수문자가 많은 것
            (r'.*[-:/]{2,}.*', '특수문자 과다'),
            
            # 5. 명확히 식재료가 아닌 것들
            (r'.*쇼핑백.*', '식재료 아님'),
            (r'.*커버.*', '식재료 아님'),
            (r'.*대여.*', '식재료 아님'),
            (r'.*포장.*', '식재료 아님'),
            
            # 6. 공백이나 구두점이 이상한 것
            (r'.*\s{3,}.*', '공백 과다'),
        ]
        
        # 명시적인 노이즈 리스트 (로그에서 발견된 것들)
        explicit_noise = [
            "노브랜드 곳밀크우",
            "스마트일들망복커버",
            "포스틱",
            "올리브 짜파게티",
            "산달기 500a/박스",
            "G 서멩여워터-NY",
            "대여용부직모쇼핑백",
            "오두기 콤비네이선:",
            "바리스타 소콜리 32",
            "미니 드레싱",
            "곳밀크",
            "곧밀크",
        ]
        
        to_delete = []
        
        # 명시적 노이즈 검색
        for noise_name in explicit_noise:
            items = IngredientMaster.objects.filter(name__icontains=noise_name)
            for item in items:
                if item not in to_delete:
                    to_delete.append(item)
                    self.stdout.write(f'  [X] 발견: "{item.name}" (명시적 노이즈)')
        
        # 패턴 기반 검색
        all_ingredients = IngredientMaster.objects.filter(api_source='UserScan')
        
        for ingredient in all_ingredients:
            name = ingredient.name
            
            # 각 패턴에 대해 검사
            for pattern, reason in noise_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    if ingredient not in to_delete:
                        to_delete.append(ingredient)
                        self.stdout.write(f'  [X] 발견: "{name}" ({reason})')
                    break
        
        # 확인 및 삭제
        if not to_delete:
            self.stdout.write(self.style.SUCCESS('\n[OK] 노이즈 데이터가 없습니다!'))
            return
        
        self.stdout.write(f'\n총 {len(to_delete)}개의 노이즈 데이터 발견')
        self.stdout.write('삭제할 항목들:')
        for item in to_delete:
            self.stdout.write(f'  - {item.name} (카테고리: {item.category}, 출처: {item.api_source})')
        
        # 사용자 확인
        confirm = input('\n정말 삭제하시겠습니까? (yes/no): ')
        
        if confirm.lower() in ['yes', 'y']:
            count = len(to_delete)
            for item in to_delete:
                item.delete()
            self.stdout.write(self.style.SUCCESS(f'\n[OK] {count}개 항목 삭제 완료!'))
        else:
            self.stdout.write(self.style.WARNING('\n취소되었습니다.'))
