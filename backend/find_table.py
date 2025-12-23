import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 테이블 이름 찾기
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ingredient%'").fetchall()
print("찾은 테이블:")
for t in tables:
    print(f"  - {t[0]}")

# master로 시작하는 테이블 찾기  
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'master%'").fetchall()
print("\nmaster로 시작하는 테이블:")
for t in tables:
    print(f"  - {t[0]}")

conn.close()
