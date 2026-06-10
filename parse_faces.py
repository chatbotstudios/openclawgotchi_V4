import re

with open('src/ui/faces.py', 'r') as f:
    lines = f.readlines()

categories = []
current_category = None
keys = []

in_dict = False

for line in lines:
    if 'DEFAULT_FACES = {' in line:
        in_dict = True
        continue
    
    if not in_dict:
        continue
        
    if line.strip() == '}':
        if current_category:
            categories.append((current_category, keys))
        break

    line = line.strip()
    if line.startswith('# ==='):
        if current_category:
            categories.append((current_category, keys))
        current_category = line
        keys = []
    elif line.startswith('"') and ':' in line:
        key = line.split('"')[1]
        keys.append(key)

for cat, k in categories:
    print(f"{cat}")
    print(", ".join(k))
    print()

