
import re
from django.core.management.base import BaseCommand
from recipes.models import RecipeIngredient
from master.models import IngredientMaster

class Command(BaseCommand):
    help = '레시피 재료 데이터 정제 (사과작은것 -> 사과 등 수식어 제거)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n--- 🧹 레시피 재료 데이터 정문화(Normalization) 시작 ---'))
        
        ingredients = RecipeIngredient.objects.all()
        total = ingredients.count()
        updated = 0
        
        # 1. 제거할 노이즈 키워드 리스트
        noise_keywords = [
            '작은것', '큰것', '중간것', '작은 것', '큰 것', '중간 것', 
            '다진', '삶은', '으깬', '볶은', '튀긴', '절인', '불린',
            '국산', '수입산', '냉동', '싱싱한', '적당량', '약간', '용'
        ]
        
        # 2. 제거할 단위 리스트
        units = ['개', '마리', '봉지', '줄기', '쪽', '알', 'g', 'ml', 'kg', 'L', '큰술', '작은술', '컵']

        for idx, ing in enumerate(ingredients, 1):
            original_name = ing.name
            name = original_name
            
            # (1) 괄호 제거
            name = re.sub(r'\(.*?\)', '', name)
            name = re.sub(r'\[.*?\]', '', name)
            
            # (2) 노이즈 키워드 제거
            for noise in noise_keywords:
                name = name.replace(noise, '')
            
            # (3) 숫자 및 단위 제거 (예: "사과 1/2개" -> "사과")
            # 숫자+단위 패턴
            name = re.sub(r'\d*\.?\d+[' + ''.join(units) + r']+', '', name)
            # 분수 패턴
            name = re.sub(r'\d+/\d+[' + ''.join(units) + r']*', '', name)
            # 그냥 숫자
            name = re.sub(r'\d+', '', name)
            
            # (4) 특수문자 및 공백 정리
            name = re.sub(r'[^가-힣]', ' ', name).strip()
            name = name.split()[0] if name.split() else "" # 첫 단어만 취함 (보통 이게 재료명)
            
            if not name:
                continue

            # (5) 마스터 DB와 매칭되면 마스터 이름으로 통일
            # 예: "청오이" -> "오이" (IngredientMaster에 오이가 있다면)
            master_match = IngredientMaster.objects.filter(name__icontains=name).first()
            if master_match:
                # 마스터 이름이 더 짧거나(표준), 괄호를 제외한 이름이 일치하면 변경
                pure_master = re.sub(r'\(.*?\)', '', master_match.name).strip()
                name = pure_master

            if name != original_name and name != "":
                ing.name = name
                ing.save()
                updated += 1
                
            if idx % 100 == 0:
                self.stdout.write(f'   - {idx}/{total} 처리 중...')

        self.stdout.write(self.style.SUCCESS(f'\n--- ✨ 완료: {updated}개의 레시피 재료가 정제되었습니다. ---\n'))
