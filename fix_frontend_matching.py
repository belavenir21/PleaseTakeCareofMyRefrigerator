"""
프론트엔드 매칭 로직도 완전 일치로 변경
"""
file_path = r'frontend\src\views\recipe\RecipeDetailView.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 부분 일치 로직
old_code = """function hasIngredient(ingredientName) {
  const normalized = normalizeText(ingredientName)
  
  // 직접 매칭
  for (const myIng of myIngredientNames.value) {
    if (myIng.includes(normalized) || normalized.includes(myIng)) {
      return true
    }
  }
  
  // 동의어 매칭
  for (const [key, values] of Object.entries(synonyms)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      for (const myIng of myIngredientNames.value) {
        if (values.some(v => myIng.includes(v) || v.includes(myIng))) {
          return true
        }
      }
    }
  }
  
  return false
}"""

# 완전 일치 로직
new_code = """function hasIngredient(ingredientName) {
  const normalized = normalizeText(ingredientName)
  
  // 완전 일치만 (백엔드와 동일한 로직)
  for (const myIng of myIngredientNames.value) {
    if (myIng === normalized) {
      return true
    }
  }
  
  // 동의어 매칭 (완전 일치만)
  for (const [key, values] of Object.entries(synonyms)) {
    if (normalized === key) {
      for (const myIng of myIngredientNames.value) {
        if (values.includes(myIng)) {
          return true
        }
      }
    }
  }
  
  return false
}"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Frontend matching changed to exact match!")
else:
    print("ERROR: Code not found")
    if 'hasIngredient' in content:
        print("  Found hasIngredient function")
    if 'myIng.includes(normalized)' in content:
        print("  Found partial match code")
