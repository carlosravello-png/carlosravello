import os
import re

base_dir = r"c:\Users\RAVELLO CAMACHO\Documents\GitHub\carlosravello"

files = [
    "el-perfil-que-no-escribiste.html",
    "the-profile-you-didnt-write.html",
    "produccion-academica/el-perfil-que-no-escribiste.html",
    "research/the-profile-you-didnt-write.html"
]

for f in files:
    path = os.path.join(base_dir, f)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace -dark.svg with .svg for el-perfil
    content = content.replace("-dark.svg", ".svg")
        
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Fixed {f}")
