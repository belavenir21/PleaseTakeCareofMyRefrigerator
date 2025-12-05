from django.core.management.base import BaseCommand
from recipes.models import Recipe, RecipeIngredient, CookingStep
from master.models import IngredientMaster

class Command(BaseCommand):
    help = 'Initialize simple recipes for beginners (Verified Data)'

    def handle(self, *args, **options):
        self.stdout.write('🍳 Adding verified simple recipes...')

        # 검색된 실제 레시피 데이터
        simple_recipes = [
            {
                'name': '간장계란밥',
                'description': '자취생의 영원한 친구, 3분 완성 초간단 요리',
                'cooking_time': 5,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Tamago_kake_gohan_by_shibainu.jpg/640px-Tamago_kake_gohan_by_shibainu.jpg',
                'ingredients': [
                    ('밥', '1공기'),
                    ('계란', '1개'),
                    ('진간장', '1큰술'),
                    ('참기름', '1큰술'),
                    ('깨', '약간'),
                    ('대파', '약간'),
                ],
                'steps': [
                    '따뜻한 밥을 그릇에 담습니다.',
                    '프라이팬에 식용유를 두르고 계란 후라이를 반숙으로 만듭니다.',
                    '밥 위에 계란 후라이를 올립니다.',
                    '진간장 1큰술과 참기름 1큰술을 뿌립니다.',
                    '깨와 송송 썬 대파를 올리고 노른자를 터뜨려 비벼 먹습니다.'
                ]
            },
            {
                'name': '김치볶음밥',
                'description': '냉장고 털기 딱 좋은 매콤한 볶음밥',
                'cooking_time': 15,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/e/ee/Kimchi_fried_rice.jpg',
                'ingredients': [
                    ('밥', '1공기'),
                    ('김치', '1컵'),
                    ('대파', '1/2대'),
                    ('계란', '1개'),
                    ('진간장', '1큰술'),
                    ('설탕', '0.5큰술'),
                    ('참기름', '1큰술'),
                ],
                'steps': [
                    '김치와 대파를 잘게 썰어 준비합니다.',
                    '프라이팬에 식용유를 두르고 대파를 볶아 파기름을 냅니다.',
                    '김치를 넣고 설탕 0.5큰술을 넣어 볶습니다.',
                    '밥을 넣고 진간장 1큰술을 넣어 잘 섞어가며 볶습니다.',
                    '마지막에 참기름을 두르고 계란 후라이를 올려 완성합니다.'
                ]
            },
            {
                'name': '참치마요덮밥',
                'description': '한솥도시락 그 맛! 고소하고 짭짤한 덮밥',
                'cooking_time': 10,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://images.unsplash.com/photo-1630409346824-4f0e7b0400d4?q=80&w=800&auto=format&fit=crop',
                'ingredients': [
                    ('밥', '1공기'),
                    ('참치', '1캔'),
                    ('계란', '2개'),
                    ('마요네즈', '적당량'),
                    ('김', '약간'),
                    ('간장', '1큰술'),
                    ('설탕', '0.5큰술'),
                ],
                'steps': [
                    '참치캔의 기름을 제거합니다.',
                    '계란은 풀어서 스크램블 에그를 만듭니다.',
                    '그릇에 밥을 담고 스크램블 에그를 가장자리에 두릅니다.',
                    '가운데에 기름 뺀 참치를 올립니다.',
                    '간장과 설탕을 섞은 소스를 뿌리고 마요네즈와 김가루를 올리면 완성!'
                ]
            },
            {
                'name': '스팸계란밥',
                'description': '전자레인지로 만드는 초간단 밥도둑',
                'cooking_time': 5,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://images.unsplash.com/photo-1599122759360-639a0352727d?q=80&w=800&auto=format&fit=crop',
                'ingredients': [
                    ('밥', '1공기'),
                    ('스팸', '1/4캔'),
                    ('계란', '2개'),
                    ('대파', '약간'),
                    ('진간장', '1큰술'),
                    ('참기름', '1큰술'),
                ],
                'steps': [
                    '스팸과 대파를 잘게 썰어 준비합니다.',
                    '전자레인지 용기에 밥을 담고 스팸과 계란을 올립니다.',
                    '전자레인지에 2~3분 정도 돌려 익힙니다.',
                    '진간장, 참기름, 대파를 넣고 비벼 먹습니다.'
                ]
            },
            {
                'name': '팽이버섯덮밥',
                'description': '식감 좋은 팽이버섯으로 만드는 덮밥',
                'cooking_time': 10,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://images.unsplash.com/photo-1543826173-70651703c5a4?q=80&w=800&auto=format&fit=crop',
                'ingredients': [
                    ('밥', '1공기'),
                    ('팽이버섯', '1봉'),
                    ('양파', '1/2개'),
                    ('다진마늘', '1큰술'),
                    ('계란', '1개'),
                    ('간장', '2큰술'),
                    ('설탕', '1큰술'),
                ],
                'steps': [
                    '양파를 채 썰고 팽이버섯은 밑동을 자릅니다.',
                    '팬에 기름을 두르고 양파와 다진마늘을 볶습니다.',
                    '팽이버섯을 넣고 간장, 설탕으로 간을 하여 볶습니다.',
                    '밥 위에 볶은 버섯을 올리고 계란 노른자를 얹어 완성합니다.'
                ]
            },
            {
                'name': '토마토 달걀 볶음',
                'description': '다이어트에도 좋은 초간단 건강식',
                'cooking_time': 10,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Stir-fried_tomato_and_scrambled_eggs_02.jpg/640px-Stir-fried_tomato_and_scrambled_eggs_02.jpg',
                'ingredients': [
                    ('토마토', '1개'),
                    ('계란', '2개'),
                    ('소금', '약간'),
                    ('후추', '약간'),
                    ('굴소스', '0.5큰술'),
                ],
                'steps': [
                    '토마토는 먹기 좋은 크기로 썰고 계란은 풀어둡니다.',
                    '팬에 기름을 두르고 계란을 스크램블 하여 따로 덜어둡니다.',
                    '팬에 토마토를 볶다가 스크램블 한 계란을 다시 넣습니다.',
                    '굴소스 0.5큰술을 넣고 1~2분 더 볶은 후 후추를 뿌려 완성합니다.'
                ]
            },
            {
                'name': '간장버터우동',
                'description': '입맛 없을 때 딱! 고소한 버터 풍미',
                'cooking_time': 5,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://images.unsplash.com/photo-1552611052-33e04de081de?q=80&w=800&auto=format&fit=crop',
                'ingredients': [
                    ('우동면', '1개'),
                    ('간장', '1큰술'),
                    ('버터', '1큰술'),
                    ('대파', '약간'),
                    ('계란', '1개'),
                ],
                'steps': [
                    '끓는 물에 우동면을 삶아 물기를 뺍니다.',
                    '팬에 버터를 녹이고 우동면과 간장을 넣어 볶습니다.',
                    '그릇에 담고 송송 썬 대파와 계란 노른자를 올립니다.',
                    '잘 비벼서 먹습니다.'
                ]
            },
            {
                'name': '소시지 야채볶음',
                'description': '밥반찬으로 최고! 쏘야볶음',
                'cooking_time': 15,
                'difficulty': '하',
                'servings': 2,
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Sausage_bokkeum.jpg/640px-Sausage_bokkeum.jpg',
                'ingredients': [
                    ('소시지', '10개'),
                    ('양파', '1/2개'),
                    ('당근', '1/4개'),
                    ('케첩', '3큰술'),
                    ('설탕', '1큰술'),
                    ('간장', '1큰술'),
                ],
                'steps': [
                    '소시지는 칼집을 내고 채소는 한입 크기로 썹니다.',
                    '팬에 기름을 두르고 소시지와 채소를 볶습니다.',
                    '케첩, 설탕, 간장을 넣고 양념이 배도록 잘 볶아줍니다.'
                ]
            },
            {
                'name': '계란 토스트',
                'description': '바쁜 아침 든든한 한 끼',
                'cooking_time': 10,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://images.unsplash.com/photo-1525351453334-e57d588268e2?q=80&w=800&auto=format&fit=crop',
                'ingredients': [
                    ('식빵', '2장'),
                    ('계란', '1개'),
                    ('우유', '2큰술'),
                    ('설탕', '1큰술'),
                    ('버터', '1조각'),
                ],
                'steps': [
                    '계란, 우유, 설탕을 섞어 계란물을 만듭니다.',
                    '식빵을 계란물에 푹 적십니다.',
                    '팬에 버터를 녹이고 식빵을 앞뒤로 노릇하게 구워줍니다.'
                ]
            },
            {
                'name': '라면 업그레이드',
                'description': '평범한 라면을 요리처럼!',
                'cooking_time': 5,
                'difficulty': '하',
                'servings': 1,
                'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Korean.ramen-Shin.Ramyun.jpg/640px-Korean.ramen-Shin.Ramyun.jpg',
                'ingredients': [
                    ('라면', '1봉'),
                    ('계란', '1개'),
                    ('대파', '약간'),
                    ('치즈', '1장'),
                ],
                'steps': [
                    '라면을 평소대로 끓입니다.',
                    '면이 거의 익으면 계란을 넣고 대파를 넣습니다.',
                    '마지막에 치즈 한 장을 올려 녹여 먹습니다.'
                ]
            }
        ]

        for recipe_data in simple_recipes:
            recipe, created = Recipe.objects.update_or_create(
                title=recipe_data['name'],
                defaults={
                    'description': recipe_data['description'],
                    'cooking_time_minutes': recipe_data['cooking_time'],
                    'difficulty': recipe_data['difficulty'],
                    'image_url': recipe_data['image_url'],
                    'api_source': 'verified_simple_recipes'
                }
            )

            if created:
                self.stdout.write(f'Created recipe: {recipe.title}')
            else:
                self.stdout.write(f'Updated recipe: {recipe.title}')
                # 기존 재료/단계 삭제 후 재생성 (간단하게)
                recipe.ingredients.all().delete()
                recipe.steps.all().delete()

            # Ingredients
            for ing_name, qty in recipe_data['ingredients']:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=ing_name,
                    quantity=qty
                )

            # Steps
            for i, step_desc in enumerate(recipe_data['steps'], 1):
                CookingStep.objects.create(
                    recipe=recipe,
                    step_number=i,
                    description=step_desc
                )

        self.stdout.write(self.style.SUCCESS('✅ Successfully added verified simple recipes!'))
