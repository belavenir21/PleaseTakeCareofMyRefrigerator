from master.models import IngredientMaster

# 숙주를 콩나물과 동일한 이모지로 설정
sukju_names = ['숙주', '숙주나물']

for name in sukju_names:
    masters = IngredientMaster.objects.filter(name=name)
    for master in masters:
        master.icon = '🌱'  # 콩나물과 동일한 이모지
        master.save()
        print(f"✅ {master.name}의 아이콘을 🌱로 변경했습니다.")

print("\n✨ 숙주 아이콘 수정 완료!")
