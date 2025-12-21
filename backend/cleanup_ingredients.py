import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
import re

def normalize_name(name):
    if not name: return ""
    # Remove text in parentheses
    name = re.sub(r'\(.*\)', '', name)
    return name.replace(" ", "").lower()

def cleanup_master_data():
    masters = IngredientMaster.objects.all()
    seen_names = {}
    deleted_count = 0
    
    # 1. Map canonical names (e.g., '달걀(10구)' -> '달걀')
    for m in masters:
        norm = normalize_name(m.name)
        if norm in seen_names:
            # Duplicate found! Keep the one with a shorter original name or first one found
            keep = seen_names[norm]
            if len(m.name) < len(keep.name):
                # Current one is shorter/cleaner, so delete old seen one
                print(f"Replacing duplicate: '{keep.name}' (ID:{keep.id}) with '{m.name}' (ID:{m.id})")
                keep.delete()
                seen_names[norm] = m
                deleted_count += 1
            else:
                print(f"Deleting duplicate: '{m.name}' (ID:{m.id}) in favor of '{keep.name}' (ID:{keep.id})")
                m.delete()
                deleted_count += 1
        else:
            seen_names[norm] = m
            
    # 2. Rename entries that have parentheses to their base name if unique
    for norm, m in seen_names.items():
        if '(' in m.name:
            new_name = re.sub(r'\(.*\)', '', m.name).strip()
            if not IngredientMaster.objects.filter(name=new_name).exclude(id=m.id).exists():
                print(f"Renaming '{m.name}' -> '{new_name}'")
                m.name = new_name
                m.save()
                
    print(f"Done! Deleted {deleted_count} duplicates.")

if __name__ == "__main__":
    cleanup_master_data()
