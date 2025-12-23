import sqlite3
import sys

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

# SQLite DB 연결
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 숙주의 image_url을 콩나물.png로 업데이트
cursor.execute("""
    UPDATE ingredient_master 
    SET image_url = '/media/ingredient_icons/콩나물.png',
        icon = '🌱'
    WHERE name IN ('숙주', '숙주나물')
""")

conn.commit()

# 확인
cursor.execute("SELECT name, icon, image_url FROM ingredient_master WHERE name IN ('숙주', '숙주나물')")
results = cursor.fetchall()

print("SUCCESS: 숙주 이미지 업데이트 완료!")
for row in results:
    print(f"  - {row[0]}: icon={row[1]}, image_url={row[2]}")

conn.close()
