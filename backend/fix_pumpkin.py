import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
updated = IngredientMaster.objects.filter(name__icontains='호박').update(icon='🎃')
print(f'Updated {updated} pumpkin items to 🎃')
