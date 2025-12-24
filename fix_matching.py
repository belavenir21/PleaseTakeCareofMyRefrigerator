"""
매칭 로직을 완전 일치로 변경
"""
file_path = r'backend\recipes\views.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 부분 일치 로직 삭제
old_code = """                    # 1. 완전 일치 우선
                    if uing in ring_variants or ring in [uing]:
                        is_matched = True
                        break
                    
                    # 2. 부분 일치 (최소 2글자 이상 & 양방향 조건 강화)
                    # - 짧은 이름("파", "양" 등)은 부분 일치 금지
                    # - 한쪽이 매우 짧으면 완전 일치만 허용
                    for v in ring_variants:
                        # 둘 다 2글자 이상일 때만 부분 일치 허용
                        if len(uing) >= 2 and len(v) >= 2:
                            # 포함 관계 확인 (더 긴 쪽에 짧은 쪽이 포함되어야 함)
                            if (len(uing) >= len(v) and v in uing) or (len(v) > len(uing) and uing in v):
                                is_matched = True
                                break
                    
                    if is_matched:
                        break"""

new_code = """                    # 완전 일치만 (동의어 포함)
                    if uing in ring_variants or ring in get_variants(uing):
                        is_matched = True
                        break"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully changed to exact match only!")
else:
    print("ERROR: Code block not found!")
    print("Searching for partial match code...")
    if '부분 일치' in content:
        print("  Found '부분 일치' in file")
    if 'len(uing) >= 2' in content:
        print("  Found 'len(uing) >= 2' in file")
