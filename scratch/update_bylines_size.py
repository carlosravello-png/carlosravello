import os
import glob
import re

files = [
    'metacognicion-2-0.html',
    'metacognition-2-0.html',
    'el-perfil-que-no-escribiste.html',
    'the-profile-you-didnt-write.html',
    'produccion-academica/metacognicion-2-0.html',
    'produccion-academica/el-perfil-que-no-escribiste.html',
    'research/metacognition-2-0.html',
    'research/the-profile-you-didnt-write.html'
]

css_old = r'''        \.author-byline img \{
            width: 80px;
            height: 106px;
            border-radius: 0;
            object-fit: cover;
            object-position: center 10%;
            border: none;
            flex-shrink: 0;
            display: block;
        \}'''

css_new = '''        .author-byline img {
            width: 140px;
            height: 190px;
            border-radius: 0;
            object-fit: cover;
            object-position: center 15%;
            border: none;
            flex-shrink: 0;
            display: block;
        }'''

# Also update the gap in .author-byline
gap_old = r'''        \.author-byline \{
            display: flex;
            align-items: center;
            gap: 18px;'''

gap_new = '''        .author-byline {
            display: flex;
            align-items: center;
            gap: 32px;'''

# And increase the font size of the name slightly to match the larger image
name_old = r'''<strong style="color:var\(--white\); font-family:var\(--serif\); font-size: 1\.1rem; font-weight: 400; letter-spacing: -0\.02em;">'''
name_new = '''<strong style="color:var(--white); font-family:var(--serif); font-size: 1.35rem; font-weight: 400; letter-spacing: -0.02em;">'''

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = re.sub(css_old, css_new, content)
    content = re.sub(gap_old, gap_new, content)
    content = re.sub(name_old, name_new, content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
