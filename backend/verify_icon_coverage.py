import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def verify_coverage():
    base_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    files = {os.path.splitext(f)[0]: f for f in os.listdir(base_dir) if f.endswith('.png')}
    
    all_masters = IngredientMaster.objects.all()
    
    no_icon = []
    no_image = []
    has_both = []
    
    for master in all_masters:
        has_emoji = master.icon and master.icon != '📦'
        has_image = bool(master.image_url)
        
        if not has_emoji and not has_image:
            no_icon.append(master.name)
        elif has_emoji and not has_image:
            no_image.append(master.name)
        elif has_both:
            has_both.append(master.name)
    
    print(f"=== 아이콘 적용 현황 ===")
    print(f"총 재료 수: {all_masters.count()}")
    print(f"아이콘/이미지 둘 다 없음: {len(no_icon)}개")
    print(f"이모지만 있음(이미지 없음): {len(no_image)}개")
    print(f"\n【둘 다 없는 재료 목록 (상위 30개)】")
    for name in no_icon[:30]:
        print(f"  - {name}")
    
    print(f"\n【이미지가 없지만 매칭 가능한 파일 존재 (상위 20개)】")
    count = 0
    for name in no_image[:50]:
        matching = [f for f in files.keys() if name in f or f in name]
        if matching:
            print(f"  - {name} → 가능한 파일: {matching}")
            count += 1
        if count >= 20:
            break

if __name__ == "__main__":
    verify_coverage()
