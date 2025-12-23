import sqlite3

# DB 연결
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 숙주의 image_url 업데이트
cursor.execute("""
    UPDATE ingredient_master
    SET image_url = 'ingredient_icons/콩나물.png'
    WHERE name = '숙주'
""")

# 변경사항 커밋
conn.commit()

# 확인
cursor.execute("SELECT name, icon, image_url FROM ingredient_master WHERE name = '숙주'")
result = cursor.fetchone()
print(f"업데이트 완료!")
print(f"이름: {result[0]}")
print(f"아이콘: {result[1]}")
print(f"이미지 URL: {result[2]}")

conn.close()
