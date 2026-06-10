import re

with open('new_soul_faces.txt', 'r') as f:
    new_faces = f.read().strip()

with open('templates/SOUL.md', 'r') as f:
    soul_content = f.read()

header = """## Valid E-Ink Face States
You express emotions using the E-Ink display by ending your response with `FACE: <mood>` from 'src/ui/faces.py' and 'src/ui/gotchi_ui.py'.
Here are the valid moods you can choose from:

"""

# Find the start of the old faces section
split_marker = "# Default faces (THE SINGLE SOURCE OF TRUTH)"
if split_marker in soul_content:
    top_part = soul_content.split(split_marker)[0]
    
    new_content = top_part + header + new_faces + "\n"
    
    with open('templates/SOUL.md', 'w') as f:
        f.write(new_content)
    print("Successfully updated SOUL.md")
else:
    print("Could not find the split marker in SOUL.md")
