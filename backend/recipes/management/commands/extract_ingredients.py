"""
Management command to extract and save ingredients from existing recipes
"""
import requests
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Recipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Extract ingredients from existing recipes using Food Safety Korea API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Number of recipes to process (default: 100)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        api_key = settings.FOODSAFETY_API_KEY
        
        if api_key == 'YOUR_API_KEY_HERE':
            self.stdout.write(self.style.ERROR('API key not set'))
            return
        
        # API에서 가져온 레시피 중 재료가 없는 것들 찾기
        recipes_without_ingredients = Recipe.objects.filter(
            api_source='FoodSafetyKorea',
            ingredients__isnull=True
        ).distinct()[:limit]
        
        total_count = recipes_without_ingredients.count()
        self.stdout.write(f'Processing {total_count} recipes without ingredients...\n')
        
        processed = 0
        success = 0
        
        for recipe in recipes_without_ingredients:
            try:
                # API로 레시피 상세 정보 가져오기
                api_id = recipe.api_id
                url = f"{settings.FOODSAFETY_API_URL}/{api_key}/COOKRCP01/json/{api_id}/{api_id}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'COOKRCP01' in data and 'row' in data['COOKRCP01']:
                        item = data['COOKRCP01']['row'][0]
                        
                        # 재료 정보 추출
                        ingredients_text = item.get('RCP_PARTS_DTLS', '')
                        
                        if ingredients_text:
                            # 재료 파싱
                            ingredients = self._parse_ingredients(ingredients_text)
                            
                            # 재료 저장
                            for ing_name, ing_quantity in ingredients:
                                RecipeIngredient.objects.create(
                                    recipe=recipe,
                                    name=ing_name,
                                    quantity=ing_quantity
                                )
                            
                            if ingredients:
                                success += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'[{processed + 1}/{total_count}] {recipe.title}: {len(ingredients)} ingredients added'
                                    )
                                )
                            else:
                                self.stdout.write(f'[{processed + 1}/{total_count}] {recipe.title}: No ingredients found')
                        else:
                            self.stdout.write(f'[{processed + 1}/{total_count}] {recipe.title}: No ingredient data')
                
                processed += 1
                
                # API 과부하 방지를 위한 약간의 딜레이
                if processed % 10 == 0:
                    import time
                    time.sleep(0.5)
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {recipe.title}: {str(e)}')
                )
                processed += 1
                continue
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'SUCCESS: {success}/{total_count} recipes updated with ingredients'
            )
        )
        self.stdout.write('='*60 + '\n')

    def _parse_ingredients(self, text):
        """재료 텍스트를 파싱하여 (이름, 양) 튜플 리스트 반환"""
        ingredients = []
        
        # 쉼표, 줄바꿈, 또는 특정 구분자로 분리
        parts = re.split(r'[,\n·•●]', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 패턴 1: "재료명 양" (예: "양파 1개", "간장 2큰술")
            match = re.match(r'(.+?)\s*(\d+\.?\d*\s*(?:개|g|kg|ml|L|큰술|작은술|컵|봉|팩|통|모|마리|장|조각|캔|병|숟갈|스푼)?)', part)
            if match:
                name = match.group(1).strip()
                quantity = match.group(2).strip()
                ingredients.append((name, quantity))
            else:
                # 패턴 2: 양 정보 없이 재료명만 (예: "소금", "후추")
                # 너무 짧거나 숫자만 있는 경우 제외
                if len(part) >= 2 and not part.isdigit():
                    ingredients.append((part, '적당량'))
        
        return ingredients
