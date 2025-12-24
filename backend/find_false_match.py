import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from refrigerator.models import UserIngredient
from django.contrib.auth.models import User

yushi = User.objects.get(username='yushi')
ings = UserIngredient.objects.filter(user=yushi).order_by('name')

print(f"Yushi's all {ings.count()} ingredients:")
for ing in ings:
    clean = ing.name.replace(" ", "").lower()
    print(f"  {ing.id:3d} | {ing.name:15s} | cleaned: {clean}")

print("\n\nSearching for matches:")
targets = ['소금', '소스', '두부', '햄']
for target in targets:
    target_clean = target.replace(" ", "").lower()
    print(f"\nTarget: '{target}' (cleaned: '{target_clean}')")
    matches = []
    for ing in ings:
        clean = ing.name.replace(" ", "").lower()
        # 현재 매칭 로직 (부분 일치)
        if target_clean in clean or clean in target_clean:
            matches.append(f"  - {ing.name} (cleaned: {clean})")
    
    if matches:
        print(f"  MATCHED:")
        for m in matches:
            print(m)
    else:
        print(f"  NO MATCH")
