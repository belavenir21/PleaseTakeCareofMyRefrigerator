"""
API Response Test - yushi 계정의 보관함 데이터 확인
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from refrigerator.serializers import UserIngredientSerializer
from refrigerator.models import UserIngredient

# yushi 사용자
yushi = User.objects.get(username='yushi')
print(f"User: {yushi.username} (ID: {yushi.id})")

# yushi의 모든 재료
ingredients = UserIngredient.objects.filter(user=yushi).order_by('-created_at')
print(f"\nTotal ingredients for yushi: {ingredients.count()}")

# Serializer로 변환 (API가 반환하는 것과 동일)
serializer = UserIngredientSerializer(ingredients, many=True)
data = serializer.data

print("\n" + "="*80)
print("API RESPONSE (What frontend should receive):")
print("="*80)
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n" + "="*80)
print("SIMPLE LIST:")
print("="*80)
for item in data:
    print(f"ID: {item['id']} | Name: {item['name']} | Qty: {item['quantity']}{item['unit']} | "
          f"Category: {item['category']} | Expiry: {item['expiry_date']}")
