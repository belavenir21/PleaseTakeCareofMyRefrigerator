import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def fix_sprouts():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    files = os.listdir(base_dir)
    
    # 숙주 관련 파일 찾기
    sukju_icon = None
    for f in files:
        if '숙주' in f:
            sukju_icon = f
            break
    
    # 콩나물 관련 파일 찾기
    kong_icon = None
    for f in files:
        if '콩나물' in f:
            kong_icon = f
            break
            
    # 사용자 요청: 숙주나물이랑 콩나물이랑 같은 아이콘 쓰기
    # 우선 순위: 숙주 아이콘이 있으면 그걸 쓰고, 없으면 콩나물 아이콘을 공통으로 사용
    common_icon = sukju_icon if sukju_icon else kong_icon
    
    if not common_icon:
        print("No sprout icons found!")
        return

    icon_path = f"/media/ingredient_icons/{common_icon}"
    
    # DB 업데이트
    names_to_update = ['숙주', '숙주나물', '콩나물']
    for name in names_to_update:
        master = IngredientMaster.objects.filter(name=name).first()
        if master:
            master.image_url = icon_path
            master.icon = '🌱' # 새싹 이모지 공통 적용
            master.save()
            print(f"Updated {name} with icon {icon_path}")
        else:
            # 존재하지 않으면 생성 (숙주나물이 없을 경우를 위해)
            if name == '숙주나물':
                IngredientMaster.objects.create(
                    name=name,
                    category='채소',
                    image_url=icon_path,
                    icon='🌱'
                )
                print(f"Created missing master entry: {name}")

if __name__ == "__main__":
    fix_sprouts()
