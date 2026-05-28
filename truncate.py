import sys
src = r'D:\hospital_pms\hospital_pms\write_login.py'
with open(src, 'r', encoding='utf-8') as f:
    lines = f.readlines()
# Keep only first 404 lines
with open(src, 'w', encoding='utf-8') as f:
    f.writelines(lines[:404])
print(f"Truncated to {len(lines[:404])} lines")
