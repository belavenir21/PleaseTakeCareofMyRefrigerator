import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def fix_sukju_icon():
    # 1. 콩나물 마스터를 찾아서 정보를 가져옴
    kong_master = IngredientMaster.objects.filter(name='콩나물').first()
    if not kong_master:
        print("콩나물 데이터를 찾을 수 없습니다.")
        return
        
    kong_image = kong_master.image_url
    print(f"콩나물 아이콘 경로: {kong_image}")

    # 2. 숙주 마스터를 찾아서 콩나물과 똑같이 맞춤
    sukju_masters = IngredientMaster.objects.filter(name__icontains='숙주')
    for master in sukju_masters:
        master.image_url = kong_image
        master.icon = '🌱' # 콩나물과 같은 '내추럴' 이모지
        master.save()
        print(f"숙주({master.name}) 아이콘을 {kong_image}로 변경 완료!")

if __name__ == "__main__":
    fix_sukju_icon()
