import sys

# PantryView.vue에서 onActivated 제거
file_path = r'frontend\src\views\refrigerator\PantryView.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# onActivated 블록 완전히 제거
old_code = """// 보관함 페이지 재진입 시 자동 새로고침 (재료 추가 후 바로 반영)
onActivated(() => {
  console.log('[PantryView] Activated - Refreshing')
  refrigeratorStore.fetchIngredients()
})"""

new_code = """// 페이지 재진입 시 자동 새로고침
const route = useRoute()
let lastPath = ''
watch(() => route.fullPath, (newPath) => {
  if (newPath.includes('/refrigerator/pantry') && lastPath && !lastPath.includes('/refrigerator/pantry')) {
    console.log('[PantryView] Returned - Refreshing')
    refrigeratorStore.fetchIngredients()
  }
  lastPath = newPath
})"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("onActivated successfully removed!")
else:
    print("onActivated block not found - searching...")
    if 'onActivated' in content:
        print("WARNING: onActivated still exists in file!")
    else:
        print("onActivated not found in file")
