import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def dump_master_names():
    with open('master_names.txt', 'w', encoding='utf-8') as f:
        for m in IngredientMaster.objects.all().order_by('name'):
            f.write(f"{m.name}\n")

if __name__ == "__main__":
    dump_master_names()
