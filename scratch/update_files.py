import os
import re

base_dir = r"c:\Users\RAVELLO CAMACHO\Documents\GitHub\carlosravello"

files = [
    "metacognicion-2-0.html",
    "metacognition-2-0.html",
    "produccion-academica/metacognicion-2-0.html",
    "research/metacognition-2-0.html",
    "el-perfil-que-no-escribiste.html",
    "the-profile-you-didnt-write.html",
    "produccion-academica/el-perfil-que-no-escribiste.html",
    "research/the-profile-you-didnt-write.html"
]

def fix_css(content):
    content = re.sub(
        r'(min-width:\s*)960px(;\s*width:\s*)960px(;)',
        r'min-width: 0\g<2>100%;\n            height: auto\g<3>',
        content
    )
    return content

def fix_author_image(content):
    # En todas las publicaciones científicas (y divulgación) usar foto secundaria
    content = re.sub(
        r'(<img src="/fotos-carlos-ravello/)foto-primaria-carlos-eduardo-ravello-joo\.webp(")',
        r'\g<1>foto-secundaria-carlos-eduardo-ravello-joo.webp\2',
        content
    )
    return content

def add_wikimedia_link(match):
    svg_path = match.group(1)
    filename = os.path.basename(svg_path).replace('-dark', '')
    wikimedia_url = f"https://commons.wikimedia.org/wiki/File:{filename.capitalize()}"
    figcaption = match.group(2)
    if 'Wikimedia Commons' not in figcaption:
        figcaption = figcaption.replace('</figcaption>', f' · <a href="{wikimedia_url}" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>')
    return match.group(0).replace(match.group(2), figcaption)

for f in files:
    path = os.path.join(base_dir, f)
    if not os.path.exists(path):
        continue
    
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    content = fix_css(content)
    content = fix_author_image(content)
    
    content = re.sub(r'<figure class="paper-fig".*?<img src="([^"]+)".*?(<figcaption>.*?</figcaption>)', add_wikimedia_link, content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Processed {f}")
