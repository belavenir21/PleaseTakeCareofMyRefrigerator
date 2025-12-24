"""
API 응답 시뮬레이션 - yushi의 보관함 데이터 확인
"""
import os, django, json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from refrigerator.serializers import UserIngredientSerializer
from refrigerator.models import UserIngredient

yushi = User.objects.get(username='yushi')
ingredients = UserIngredient.objects.filter(user=yushi).order_by('-created_at')

print(f"Total: {ingredients.count()}")
print("\nAPI Response (first 10):")

serializer = UserIngredientSerializer(ingredients[:10], many=True)
for item in serializer.data:
    print(f"  ID:{item['id']:3d} | {item['name']:15s} | Cat: {item.get('category', 'None'):10s}")

# 레몬청 찾기
lemon = ingredients.filter(name__contains='레몬').first()
if lemon:
    print(f"\nLEMON FOUND IN DB:")
    print(f"  ID: {lemon.id}")
    print(f"  Name: {lemon.name}")
    print(f"  Category: {lemon.category}")
    print(f"  Created: {lemon.created_at}")
    
    # Serializer로 변환
    s = UserIngredientSerializer(lemon)
    print(f"\nSerialized:")
    for k, v in s.data.items():
        print(f"  {k}: {v}")
else:
    print("\nLEMON NOT FOUND!")

# 모든 재료 이름 출력
print(f"\nAll {ingredients.count()} ingredients:")
for ing in ingredients:
    print(f"  {ing.id:3d} | {ing.name}")
