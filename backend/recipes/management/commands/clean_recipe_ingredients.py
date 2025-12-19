"""
재료 데이터 정제 명령어
- 괄호 및 괄호 내 내용 제거
- 불필요한 접두사 제거 (양념:, 머랭>, 등)
- 수량과 이름 분리
"""
import re
from django.core.management.base import BaseCommand
from recipes.models import RecipeIngredient
from master.models import IngredientMaster
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = '레시피 재료 데이터 정제 (괄호, 특수문자, 불필요한 설명 제거)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 저장하지 않고 변경 사항만 출력'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('[INFO] 레시피 재료 데이터 정제 시작...\n')
        
        all_ingredients = RecipeIngredient.objects.all()
        total_count = all_ingredients.count()
        updated_count = 0
        
        for idx, ingredient in enumerate(all_ingredients, 1):
            original_name = ingredient.name
            original_quantity = ingredient.quantity
            
            # 1단계: 재료명 정제
            cleaned_name = self.clean_ingredient_name(original_name)
            
            # 2단계: 수량 정제
            cleaned_quantity = self.clean_quantity(original_quantity, original_name)
            
            # 3단계: 재료명과 수량이 섞여있는 경우 분리
            if '(' in original_name and ')' in original_name:
                # 예: "사과(1/2개)" -> name="사과", quantity="1/2개"
                match = re.match(r'(.+?)\((.+?)\)', original_name)
                if match:
                    cleaned_name = match.group(1).strip()
                    if not cleaned_quantity or cleaned_quantity == '적당량':
                        cleaned_quantity = match.group(2).strip()
            
            # 변경 사항이 있으면 출력 및 저장
            if cleaned_name != original_name or cleaned_quantity != original_quantity:
                self.stdout.write(
                    f'[{idx}/{total_count}] [UPDATE] {ingredient.recipe.title}\n'
                    f'  이름: "{original_name}" → "{cleaned_name}"\n'
                    f'  수량: "{original_quantity}" → "{cleaned_quantity}"\n'
                )
                
                if not dry_run:
                    ingredient.name = cleaned_name
                    ingredient.quantity = cleaned_quantity
                    ingredient.save()
                
                updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY RUN] {updated_count}/{total_count} 개의 재료가 변경될 예정입니다.')
            )
            self.stdout.write('실제 적용하려면 --dry-run 옵션 없이 다시 실행하세요.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n[SUCCESS] 완료! {updated_count}/{total_count} 개의 재료를 정제했습니다.')
            )

    def clean_ingredient_name(self, name):
        """재료명 정제"""
        if not name:
            return name
        
        # 1. 불필요한 접두사 제거
        # "양념 : 올리고당" -> "올리고당"
        # "머랭>달걀흰자" -> "달걀흰자"
        patterns = [
            r'^양념\s*[:：]\s*',  # 양념: 또는 양념：
            r'^소스\s*[:：]\s*',
            r'^.*?>\s*',  # 머랭> 같은 패턴
            r'^.*?>>\s*',
        ]
        
        for pattern in patterns:
            name = re.sub(pattern, '', name)
        
        # 2. 괄호 및 괄호 내 내용 제거 (수량 정보는 제외)
        # "사과(빨간색)" -> "사과"
        # "양파(중)" -> "양파"
        # 단, 숫자가 들어있는 괄호는 quantity로 처리하므로 여기선 제거
        name = re.sub(r'\([^0-9)]*\)', '', name)
        
        # 3. 대괄호 제거
        name = re.sub(r'\[.*?\]', '', name)
        
        # 4. 특수문자 정리
        name = name.replace('_', ' ').replace('/', ' ').strip()
        
        # 5. 연속된 공백 제거
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()

    def clean_quantity(self, quantity, name):
        """수량 정제"""
        if not quantity:
            return '적당량'
        
        # 이미 깔끔한 수량인 경우 그대로 유지
        quantity = str(quantity).strip()
        
        if not quantity:
            return '적당량'
        
        return quantity


