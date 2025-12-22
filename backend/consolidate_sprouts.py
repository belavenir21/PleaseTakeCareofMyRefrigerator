import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster
from refrigerator.models import UserIngredient

def consolidate_sprouts():
    # 1. 대상 찾기
    sukju = IngredientMaster.objects.filter(name='숙주').first()
    sukju_namul = IngredientMaster.objects.filter(name='숙주나물').first()
    kong_namul = IngredientMaster.objects.filter(name='콩나물').first()

    if not sukju:
        print("Master '숙주' not found. Creating it...")
        # 만약 숙주나물만 있다면 숙주로 이름을 바꿔서 사용
        if sukju_namul:
            sukju = sukju_namul
            sukju.name = '숙주'
            sukju.save()
            sukju_namul = None
        else:
            sukju = IngredientMaster.objects.create(name='숙주', category='채소')

    # 2. 숙주나물 데이터를 숙주로 통합 (만약 숙주나물이 마스터로 지정된 유저 재료가 있다면)
    if sukju_namul and sukju_namul != sukju:
        print(f"Consolidating '{sukju_namul.name}' into '{sukju.name}'...")
        UserIngredient.objects.filter(master_ingredient=sukju_namul).update(master_ingredient=sukju)
        
        # 통합 후 중복된 마스터 데이터 삭제
        sukju_namul.delete()
        print("Deleted redundant master '숙주나물'")

    # 3. 아이콘 통일 (콩나물 아이콘을 공통으로 사용 - 사용자 요청)
    # 현재 폴더에 있는 파일 목록 확인
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    files = os.listdir(base_dir)
    
    sprout_icon = None
    # '콩나물.png' 또는 '숙주.png' 중 존재하는 것을 찾음
    for f in ['콩나물.png', '숙주.png', '숙주나물.png']:
        if f in files:
            sprout_icon = f
            break
            
    if sprout_icon:
        icon_path = f"/media/ingredient_icons/{sprout_icon}"
        
        # 숙주와 콩나물 모두에게 동일한 아이콘 적용
        sukju.image_url = icon_path
        sukju.icon = '🌱'
        sukju.save()
        
        if kong_namul:
            kong_namul.image_url = icon_path
            kong_namul.icon = '🌱'
            kong_namul.save()
            print(f"Applied icon {icon_path} to both 숙주 and 콩나물")
    else:
        print("Still no sprout icon file found in directory!")

if __name__ == "__main__":
    consolidate_sprouts()
