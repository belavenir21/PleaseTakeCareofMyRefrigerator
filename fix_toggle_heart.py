"""
토글 버튼을 하트 이모티콘으로 변경
"""
file_path = r'frontend\src\views\recipe\RecipeListView.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# HTML 수정
old_html = """              <div class="toggle-track" :class="{ active: showRecommendations }">
                <div class="toggle-thumb" :class="{ active: showRecommendations }">
                  <img :src="heartIcon" class="thumb-img-extra" />
                </div>
              </div>"""

new_html = """              <div class="toggle-track" :class="{ active: showRecommendations }">
                <div class="toggle-heart" :class="{ active: showRecommendations }">
                  🤍
                </div>
              </div>"""

if old_html in content:
    content = content.replace(old_html, new_html)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Toggle button changed to heart emoji!")
else:
    print("ERROR: HTML not found")
    if 'toggle-thumb' in content:
        print("  Found toggle-thumb")
    if 'heartIcon' in content:
        print("  Found heartIcon")
