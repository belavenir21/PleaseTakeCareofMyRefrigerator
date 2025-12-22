import os
import re
import json
import time
import requests
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Recipe, RecipeIngredient, CookingStep

class Command(BaseCommand):
    help = 'AI(Gemini)를 사용하여 레시피 재료를 재추출하고 정규화하여 DB를 갱신합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, help='처리할 레시피 개수 제한 (테스트용)')

    def handle(self, *args, **options):
        gms_key = getattr(settings, 'GMS_KEY', None)
        if not gms_key:
            self.stdout.write(self.style.ERROR('[ERROR] GMS_KEY가 설정되어 있지 않습니다.'))
            return

        recipes = Recipe.objects.all()
        limit = options.get('limit')
        if limit:
            recipes = recipes[:limit]
            
        total_count = recipes.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n--- [START] 총 {total_count}개의 레시피 작업 시작 ---\n'))

        processed_count = 0
        success_count = 0
        fail_count = 0

        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gms_key}"

        for recipe in recipes:
            processed_count += 1
            self.stdout.write(f'[{processed_count}/{total_count}] "{recipe.title}" 분석 중...', ending='')
            sys.stdout.flush() # 즉시 출력 강제

            try:
                # 1. 기존 재료 삭제 (재작업을 위해)
                recipe.ingredients.all().delete()

                # 2. 텍스트 구성
                steps_text = "\n".join([f"{step.step_number}. {step.description}" for step in recipe.steps.all().order_by('step_number')])
                full_text = f"제목: {recipe.title}\n설명: {recipe.description}\n조리단계:\n{steps_text}"

                # 3. AI 프롬프트 (정규화 및 더블체크 로직 포함)
                prompt = f"""
다음 레시피 정보를 읽고, 사용된 '재료'와 해당 '수량'을 추출하여 JSON 배열로 출력하세요.

[추출 규칙]
1. 재료명 정규화:
   - 괄호 내용 제거: "사과(부사)", "고기(안심)" -> "사과", "고기"
   - 수식어 제거: "다진마늘", "불린당면", "국산참기름" -> "마늘", "당면", "참기름" (단, "고추장", "진간장", "된장" 등 고유 명칭은 유지)
   - 띄어쓰기 지우고 순수 재료명만. (예: "식용 유" -> "식용유")
   - 특수문자 금지.
2. 수량/단위 추출:
   - 레시피에 명시된 수량과 단위를 있는 그대로 추출하세요. (예: "1/2개", "2큰술", "300g", "약간")
   - 레시피에 수량이 명시되지 않았다면 "적당량"이라고 적어주세요.
3. 더블 체크:
   - 실제로 해당 요리 과정에 필요한 **식재료**인지 확인하세요.
   - 조리 도구(냄비, 팬), 불필요한 장식 등은 제외하세요.

응답 형식:
반드시 JSON 객체의 배열이어야 합니다. 마크다운 코드 블록(```json)을 사용하지 마세요.
예시: [{{"name": "김치", "quantity": "1/4포기"}}, {{"name": "돼지고기", "quantity": "200g"}}]

레시피 내용:
{full_text}
"""

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }

                # 4. API 요청
                start_time = time.time()
                response = requests.post(url, json=payload, timeout=45)
                elapsed = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    raw_content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # JSON 추출
                    clean_json = re.sub(r'```json\s*|\s*```', '', raw_content).strip()
                    match_list = re.search(r'\[.*\]', clean_json, re.DOTALL)
                    if match_list:
                        clean_json = match_list.group(0)
                    
                    ingredients_list = json.loads(clean_json)

                    # 5. 저장
                    ing_count = 0
                    for item in ingredients_list:
                        name = item.get('name', '').strip()
                        quantity = item.get('quantity', '적당량').strip()
                        
                        if name and not RecipeIngredient.objects.filter(recipe=recipe, name=name).exists():
                            RecipeIngredient.objects.create(
                                recipe=recipe, 
                                name=name, 
                                quantity=quantity
                            )
                            ing_count += 1
                    
                    self.stdout.write(self.style.SUCCESS(f' -> 완료 ({ing_count}개 추출, {elapsed:.1f}초)'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f' -> API 에러 ({response.status_code})'))
                    fail_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f' -> 오류 발생: {str(e)}'))
                fail_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n--- [FINISH] 성공: {success_count}, 실패: {fail_count} ---\n'))
