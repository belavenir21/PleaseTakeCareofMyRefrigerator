"""
재료 추가 테스트 스크립트
"""
import os
import django
import json
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from refrigerator.models import UserIngredient

print("\n" + "="*80)
print("INGREDIENT ADD TEST")
print("="*80)

# 테스트 사용자 (최근 가입한 사용자 또는 특정 사용자)
test_user = User.objects.filter(username='belavenir21').first()
if not test_user:
    test_user = User.objects.first()

print(f"\nTest User: {test_user.username}")
print(f"Current ingredients: {UserIngredient.objects.filter(user=test_user).count()}")

# 기존 재료 출력
print("\n[BEFORE TEST]")
before_items = UserIngredient.objects.filter(user=test_user).order_by('-created_at')[:5]
for item in before_items:
    print(f"  - {item.name} ({item.quantity}{item.unit}) | Created: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

# 테스트 재료 추가
print("\n[ADDING TEST INGREDIENT]")
test_ing = UserIngredient.objects.create(
    user=test_user,
    name="테스트양파",
    quantity=2.0,
    unit="개",
    category="채소",
    storage_method="냉장",
    expiry_date=date.today() + timedelta(days=7)
)
print(f"  ✅ Added: {test_ing.name} (ID: {test_ing.id})")

# 추가 후 확인
print("\n[AFTER TEST]")
after_items = UserIngredient.objects.filter(user=test_user).order_by('-created_at')[:5]
for item in after_items:
    print(f"  - {item.name} ({item.quantity}{item.unit}) | Created: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\nTotal ingredients now: {UserIngredient.objects.filter(user=test_user).count()}")

# API 테스트 (serializer가 제대로 작동하는지)
print("\n[SERIALIZER TEST]")
from refrigerator.serializers import UserIngredientSerializer
serializer = UserIngredientSerializer(test_ing)
print("Serialized data:")
print(json.dumps(serializer.data, indent=2, ensure_ascii=False))

# 최근 추가된 전체 재료
print("\n[ALL RECENT INGREDIENTS (All Users)]")
recent_all = UserIngredient.objects.all().order_by('-created_at')[:10]
for r in recent_all:
    print(f"  {r.created_at.strftime('%Y-%m-%d %H:%M:%S')} | User: {r.user.username} | {r.name} ({r.quantity}{r.unit})")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
