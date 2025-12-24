import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from refrigerator.models import UserIngredient

yushi = User.objects.get(username='yushi')
ingredients = UserIngredient.objects.filter(user=yushi).order_by('-created_at')

print(f"Total for yushi: {ingredients.count()}")
print("\nRecent 10:")
for item in ingredients[:10]:
    cat = item.category or 'None'
    print(f"  {item.id} | {item.name} ({item.quantity}{item.unit}) | Cat: {cat} | Exp: {item.expiry_date}")
