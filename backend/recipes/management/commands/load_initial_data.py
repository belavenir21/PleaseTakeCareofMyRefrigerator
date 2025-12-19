"""
협업용 초기 데이터 일괄 로드
새 환경에서 한 번에 모든 초기 데이터를 불러옵니다
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = '협업용 초기 데이터 일괄 로드 (fixtures)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default='fixtures',
            help='Fixtures 디렉토리 경로 (기본: fixtures)'
        )

    def handle(self, *args, **options):
        fixtures_dir = options['fixtures_dir']
        
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('[INIT] 초기 데이터 일괄 로드 시작!'))
        self.stdout.write('='*60 + '\n')
        
        # 로드 순서 (외래키 관계 고려)
        fixtures_order = [
            ('master_ingredients.json', '[MASTER] 마스터 재료 데이터'),
            ('recipes.json', '[RECIPE] 레시피 데이터'),
            ('recipe_ingredients.json', '[INGREDIENTS] 레시피 재료 데이터'),
            ('cooking_steps.json', '[STEPS] 조리 단계 데이터'),
        ]
        
        loaded_count = 0
        
        for filename, description in fixtures_order:
            filepath = os.path.join(fixtures_dir, filename)
            
            if not os.path.exists(filepath):
                self.stdout.write(
                    self.style.WARNING(f'[SKIP] {description}: {filepath} 파일이 없습니다. 건너뜁니다.\n')
                )
                continue
            
            self.stdout.write(f'{description} 로드 중...')
            
            try:
                call_command('loaddata', filepath, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'  [OK] {filename} 로드 완료\n'))
                loaded_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [ERROR] {filename} 로드 실패: {str(e)}\n')
                )
        
        self.stdout.write('='*60)
        if loaded_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'[SUCCESS] {loaded_count}개의 fixtures 로드 완료!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('[WARNING] 로드된 fixtures가 없습니다.')
            )
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write('[NEXT] 다음 단계:')
        self.stdout.write('  - 데이터 확인: python manage.py shell')
        self.stdout.write('  - 개발 서버 실행: python manage.py runserver\n')
