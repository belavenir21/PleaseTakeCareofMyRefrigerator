"""
협업을 위한 Fixtures 내보내기
DB 데이터를 JSON 파일로 저장하여 다른 팀원들도 동일한 초기 데이터 사용 가능
"""
from django.core.management.base import BaseCommand
from django.core import serializers
from recipes.models import Recipe, RecipeIngredient, CookingStep
from master.models import IngredientMaster
import json
import os


class Command(BaseCommand):
    help = '협업을 위한 초기 데이터(fixtures) 내보내기'

    def handle(self, *args, **options):
        self.stdout.write('📦 Fixtures 내보내기 시작...\n')
        
        # Fixtures 디렉토리 생성
        fixtures_dir = 'fixtures'
        os.makedirs(fixtures_dir, exist_ok=True)
        
        # 1. 마스터 재료 데이터 내보내기
        self.export_model(
            IngredientMaster,
            f'{fixtures_dir}/master_ingredients.json',
            '🥬 마스터 재료 데이터'
        )
        
        # 2. 레시피 데이터 내보내기
        self.export_model(
            Recipe,
            f'{fixtures_dir}/recipes.json',
            '📖 레시피 데이터'
        )
        
        # 3. 레시피 재료 데이터 내보내기
        self.export_model(
            RecipeIngredient,
            f'{fixtures_dir}/recipe_ingredients.json',
            '🥘 레시피 재료 데이터'
        )
        
        # 4. 조리 단계 데이터 내보내기
        self.export_model(
            CookingStep,
            f'{fixtures_dir}/cooking_steps.json',
            '👨‍🍳 조리 단계 데이터'
        )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('✅ 모든 fixtures 내보내기 완료!')
        )
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write('📌 사용법:')
        self.stdout.write('  새 환경에서 데이터 불러오기:')
        self.stdout.write(f'    python manage.py loaddata {fixtures_dir}/master_ingredients.json')
        self.stdout.write(f'    python manage.py loaddata {fixtures_dir}/recipes.json')
        self.stdout.write(f'    python manage.py loaddata {fixtures_dir}/recipe_ingredients.json')
        self.stdout.write(f'    python manage.py loaddata {fixtures_dir}/cooking_steps.json\n')

    def export_model(self, model, filepath, description):
        """특정 모델 데이터를 JSON 파일로 내보내기"""
        queryset = model.objects.all()
        count = queryset.count()
        
        self.stdout.write(f'{description}: {count}개')
        
        if count == 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  데이터가 없어 {filepath} 파일을 생성하지 않았습니다.\n'))
            return
        
        # JSON으로 직렬화
        data = serializers.serialize('json', queryset, indent=2, ensure_ascii=False)
        
        # 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {filepath} 저장 완료\n'))
