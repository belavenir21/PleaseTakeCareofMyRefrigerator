import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from refrigerator.models import UserIngredient

# 레몬청 검색
lemon = UserIngredient.objects.filter(name__contains='레몬').order_by('-created_at')
print(f"Found {lemon.count()} items containing '레몬':")
for item in lemon:
    print(f"  ID: {item.id} | Name: {item.name} | User: {item.user.username} | "
          f"Created: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

# 최근 10개 재료 확인
print("\nLast 10 ingredients added (all users):")
recent = UserIngredient.objects.all().order_by('-created_at')[:10]
for r in recent:
    print(f"  {r.created_at.strftime('%H:%M:%S')} | {r.user.username} | {r.name} ({r.quantity}{r.unit}) | Category: {r.category}")
