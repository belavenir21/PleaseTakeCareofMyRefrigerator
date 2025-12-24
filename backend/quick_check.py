import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from refrigerator.models import UserIngredient
from django.contrib.auth.models import User

print(f"Total ingredients: {UserIngredient.objects.count()}")

latest = UserIngredient.objects.order_by('-created_at').first()
if latest:
    print(f"Latest added: {latest.name} by {latest.user.username} at {latest.created_at}")
    
# belavenir21 사용자의 재료
user = User.objects.filter(username='belavenir21').first()
if user:
    count = UserIngredient.objects.filter(user=user).count()
    print(f"\nbelavenir21's ingredients: {count}")
    recent = UserIngredient.objects.filter(user=user).order_by('-created_at')[:5]
    for r in recent:
        print(f"  - {r.name} ({r.quantity}{r.unit}) added at {r.created_at}")
