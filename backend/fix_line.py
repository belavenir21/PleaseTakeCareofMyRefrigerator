#!/usr/bin/env python
# Quick fix for final_name -> item_name in line 354
with open('refrigerator/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 354 (index 353)
if 'special_count' in lines[353] and 'final_name' in lines[353]:
    lines[353] = lines[353].replace('final_name', 'item_name')
    print("Fixed line 354")

with open('refrigerator/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Done!")
