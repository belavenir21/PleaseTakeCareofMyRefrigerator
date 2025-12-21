import os
import django
import re
from difflib import SequenceMatcher

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from refrigerator.models import UserIngredient
from master.models import IngredientMaster

def normalize_name(name):
    if not name: return ""
    name = re.sub(r'\(.*\)', '', name)
    return name.replace(" ", "").lower()

def heal_user_ingredients():
    masters = list(IngredientMaster.objects.all())
    user_ings = UserIngredient.objects.filter(master_ingredient__isnull=True)
    
    synonyms = {
        '계란': '달걀', '쇠고기': '소고기', '닭': '닭고기', '돼지': '돼지고기',
        '무우': '무', '공기밥': '밥'
    }
    
    count = 0
    for ui in user_ings:
        target = normalize_name(ui.name)
        for k, v in synonyms.items():
            if k in target: target = target.replace(k, v)
            
        best_match = None
        # 1. Exact normalized match
        for m in masters:
            if normalize_name(m.name) == target:
                best_match = m
                break
        
        # 2. Substring match
        if not best_match:
            for m in masters:
                m_norm = normalize_name(m.name)
                if m_norm in target or target in m_norm:
                    best_match = m
                    break
                    
        if best_match:
            print(f"Linking UserIngredient '{ui.name}' (ID:{ui.id}) to Master '{best_match.name}' (ID:{best_match.id})")
            ui.master_ingredient = best_match
            ui.save()
            count += 1
            
    print(f"Healed {count} user ingredients.")

if __name__ == "__main__":
    heal_user_ingredients()
