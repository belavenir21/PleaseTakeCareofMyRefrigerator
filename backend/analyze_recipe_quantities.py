"""
레시피 재료 수량 데이터 분석 (인코딩 이슈 해결 버전)
"""
import os
import django
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from recipes.models import RecipeIngredient, Recipe

print("\n=== Recipe Ingredient Quantity Analysis ===\n")

# 전체 재료 수
total = RecipeIngredient.objects.count()
print(f"Total ingredients: {total}\n")

# 수량 값 빈도 분석
quantities = list(RecipeIngredient.objects.values_list('quantity', flat=True))
counter = Counter(quantities)

print("[Top 30 Most Common Quantity Values]")
print("-" * 70)
for q, count in counter.most_common(30):
    percentage = (count / total * 100)
    print(f'  "{q}": {count} ({percentage:.1f}%)')

# "적정량" 같은 텍스트 패턴 찾기
vague_keywords = ['적당량', '적정량', '적당히', '조금', '약간', '소량', '다량', '많이', '취향껏', '기호', '필요량']
vague_count = 0
vague_examples = []

for ing in RecipeIngredient.objects.all()[:100]:  # 샘플 100개
    q = ing.quantity
    if any(keyword in q for keyword in vague_keywords):
        vague_count += 1
        if len(vague_examples) < 10:
            vague_examples.append(f"{ing.recipe.title[:20]} - {ing.name}: {q}")

print(f"\n[WARNING] Vague quantities (sample 100): {vague_count}")
if vague_examples:
    print("\nExamples:")
    for ex in vague_examples:
        print(f"  - {ex}")

# 빈 문자열 또는 None 확인
empty_count = RecipeIngredient.objects.filter(quantity__in=['', ' ', '-']).count()
print(f"\n[WARNING] Empty/dash values: {empty_count}")

# 숫자로 시작하는 vs 텍스트로 시작하는
numeric_start = 0
text_start = 0

for q in quantities[:1000]:  # 샘플 1000개
    if q and q[0].isdigit():
        numeric_start += 1
    else:
        text_start += 1

print(f"\n[Classification - Sample 1000]:")
print(f"  Starts with number: {numeric_start} ({numeric_start/10:.1f}%)")
print(f"  Starts with text: {text_start} ({text_start/10:.1f}%)")

print("\n" + "="*70)
print("\n[RECOMMENDATION]")

# 적당량/적정량 비율 계산
vague_total = counter.get('적당량', 0) + counter.get('적정량', 0)
vague_percentage = (vague_total / total * 100) if total > 0 else 0

print(f"\n'Jeokdangryang/Jeokjeongryang': {vague_total} ({vague_percentage:.1f}%)")

if vague_percentage > 30:
    print("\n  [DELETE FIELD] Over 30% are vague -> Recommend deleting 'quantity' field")
elif vague_percentage > 10:
    print("\n  [CLEAN DATA] 10-30% vague -> Consider data cleaning")
else:
    print("\n  [KEEP FIELD] Mostly specific quantities -> Recommend keeping field")

print("\n" + "="*70)
