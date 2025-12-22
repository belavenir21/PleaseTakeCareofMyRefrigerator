# -*- coding: utf-8 -*-
"""
음료/주류 이모지 수정 스크립트
- 콜라, 사이다 등 탄산음료 -> 🥤
- 맥주 -> 🍺
- 와인 -> 🍷
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from master.models import IngredientMaster

def fix_drink_icons():
    updated = []
    
    # 탄산음료/콜라/사이다 등 -> 🥤
    drink_keywords = ['콜라', '사이다', '환타', '스프라이트', '탄산', '에너지드링크', '제로']
    
    for kw in drink_keywords:
        items = IngredientMaster.objects.filter(name__icontains=kw)
        for item in items:
            # 콜라비(채소)는 제외
            if '콜라비' in item.name:
                continue
            old_icon = item.icon
            item.icon = '🥤'
            item.image_url = None  # 이모지 우선
            item.save()
            updated.append(f'{item.name}: {old_icon} -> 🥤')
    
    # 맥주 -> 🍺
    beer_items = IngredientMaster.objects.filter(name__icontains='맥주')
    for item in beer_items:
        old_icon = item.icon
        item.icon = '🍺'
        item.image_url = None
        item.save()
        updated.append(f'{item.name}: {old_icon} -> 🍺')
    
    # 와인 -> 🍷
    wine_items = IngredientMaster.objects.filter(name__icontains='와인')
    for item in wine_items:
        old_icon = item.icon
        item.icon = '🍷'
        item.image_url = None
        item.save()
        updated.append(f'{item.name}: {old_icon} -> 🍷')
    
    # 소주 -> 🍶
    soju_items = IngredientMaster.objects.filter(name__icontains='소주')
    for item in soju_items:
        old_icon = item.icon
        item.icon = '🍶'
        item.image_url = None
        item.save()
        updated.append(f'{item.name}: {old_icon} -> 🍶')
    
    print('=== 음료/주류 이모지 수정 완료 ===')
    for u in updated:
        print(f'  {u}')
    print(f'\nTotal: {len(updated)} items updated')


if __name__ == "__main__":
    fix_drink_icons()
