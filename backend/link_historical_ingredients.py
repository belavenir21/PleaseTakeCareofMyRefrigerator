import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from refrigerator.models import UserIngredient
from master.models import IngredientMaster

def link_user_ingredients():
    ingredients = UserIngredient.objects.filter(master_ingredient__isnull=True)
    count = 0
    for ing in ingredients:
        master = IngredientMaster.objects.filter(name=ing.name).first()
        if not master:
            # 대소문자 무시 매칭
            master = IngredientMaster.objects.filter(name__iexact=ing.name).first()
        
        if master:
            ing.master_ingredient = master
            ing.save()
            count += 1
            print(f"Linked: {ing.name} -> {master.name}")
    
    print(f"Total linked: {count}")

if __name__ == "__main__":
    link_user_ingredients()
