"""
CookingModeView.vue quantity 제거 스크립트
"""
import re
import os

filepath = r'c:\Users\SSAFY\Desktop\PleaseTakeCareofMyRefrigerator\frontend\src\views\recipe\CookingModeView.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 문제가 되는 부분만 교체
old_pattern = r"        // 수량이 '적당량'인 경우 기본 차감량을 1로 설정 \(추후 조절 가능\)\s*\n\s*const isAbstract = isAbstractQuantity\(ing\.quantity\)\s*\n\s*return \{\s*\n\s*id: ing\.id,\s*\n\s*name: ing\.name,\s*\n\s*unit: isAbstract \? '적정량' : \(extractUnit\(ing\.quantity\) \|\| '개'\),\s*\n\s*usedAmount: isAbstract \? 1 : \(extractNumber\(ing\.quantity\) \|\| 1\),\s*\n\s*currentStock: pantryItem\?\.quantity \|\| 0,\s*\n\s*hasInPantry: !!pantryItem,\s*\n\s*pantryId: pantryItem\?\.id\s*\n\s*\}"

new_text = """        // quantity 필드 제거됨: 모든 재료에 기본값 적용
        
        return {
          id: ing.id,
          name: ing.name,
          unit: '개',
          usedAmount: 1,
          currentStock: pantryItem?.quantity || 0,
          hasInPantry: !!pantryItem,
          pantryId: pantryItem?.id
        }"""

modified = re.sub(old_pattern, new_text, content)

if modified != content:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified)
    print("✅ Modified CookingMode View.vue successfully")
else:
    print(" ⚠️ Pattern not found, trying simple replacement...")
    # 간단한 방법으로 재시도
    if 'isAbstractQuantity(ing.quantity)' in content:
        content = content.replace('isAbstractQuantity(ing.quantity)', '// quantity removed')
        content = content.replace(
            "unit: isAbstract ? '적정량' : (extractUnit(ing.quantity) || '개'),",
            "unit: '개',"
        )
        content = content.replace(
            'usedAmount: isAbstract ? 1 : (extractNumber(ing.quantity) || 1),',
            'usedAmount: 1,'
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Modified CookingModeView.vue (simple method)")
    else:
        print("❌ Could not modify file")
