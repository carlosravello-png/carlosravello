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

# CSS replacement pattern
css_old = r'''        \.author-byline img \{
            width: 72px;
            height: 96px;
            border-radius: 0;
            object-fit: cover;
            object-position: center 5%;
            border: 1px solid var\(--border\);
            flex-shrink: 0;
            display: block;
        \}'''

css_new = '''        .author-byline img {
            width: 80px;
            height: 106px;
            border-radius: 0;
            object-fit: cover;
            object-position: center 10%;
            border: none;
            flex-shrink: 0;
            display: block;
        }'''

# HTML replacement pattern. The goal is to remove the ORCID link if it exists, and make sure the text is just Name, Role, Link
# A robust way is to find the whole <div class="author-byline"> ... </div> and replace it based on language.

html_es = '''            <div class="author-byline">
                <img src="/fotos-carlos-ravello/foto-secundaria-carlos-eduardo-ravello-joo.webp"
                     alt="Carlos Eduardo Ravello Joo"
                     width="1046" height="1600" loading="lazy">
                <div class="author-byline-text">
                    <strong style="color:var(--white); font-family:var(--serif); font-size: 1.1rem; font-weight: 400; letter-spacing: -0.02em;">Carlos Eduardo Ravello Joo</strong><br>
                    Investigador independiente · Trujillo, Perú<br>
                    <a href="/sobre-mi.html">sobre mí →</a>
                </div>
            </div>'''

html_en = '''            <div class="author-byline">
                <img src="/fotos-carlos-ravello/foto-secundaria-carlos-eduardo-ravello-joo.webp"
                     alt="Carlos Eduardo Ravello Joo"
                     width="1046" height="1600" loading="lazy">
                <div class="author-byline-text">
                    <strong style="color:var(--white); font-family:var(--serif); font-size: 1.1rem; font-weight: 400; letter-spacing: -0.02em;">Carlos Eduardo Ravello Joo</strong><br>
                    Independent researcher · Trujillo, Peru<br>
                    <a href="/about-me.html">about me →</a>
                </div>
            </div>'''

html_pattern = re.compile(r'<div class="author-byline">.*?</div>\s*</div>', re.DOTALL)
html_pattern2 = re.compile(r'<div class="author-byline">.*?</script>', re.DOTALL) # bad regex
html_pattern3 = re.compile(r'<div class="author-byline">.*?</div>\s*</div>\s*(?:</div>)?', re.DOTALL) # be careful

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update CSS
    content = re.sub(css_old, css_new, content)
    
    # Update HTML. Instead of complex regex, let's just find the author-byline div and replace the inner HTML.
    # Actually, the ORCID link part is easier to regex.
    # Remove: <a href="https://orcid.org/0009-0007-5631-7436" target="_blank" rel="me noopener">ORCID 0009-0007-5631-7436</a> ·
    
    content = re.sub(r'<a href="https://orcid\.org/0009-0007-5631-7436"[^>]*>ORCID 0009-0007-5631-7436</a>\s*·\s*', '', content)
    
    # Enhance the strong tag to match editorial style
    content = re.sub(r'<strong style="color:var\(--text\)">Carlos Eduardo Ravello Joo</strong>', r'<strong style="color:var(--white); font-family:var(--serif); font-size: 1.1rem; font-weight: 400; letter-spacing: -0.02em;">Carlos Eduardo Ravello Joo</strong>', content)
    content = re.sub(r'<strong>Carlos Eduardo Ravello Joo</strong>', r'<strong style="color:var(--white); font-family:var(--serif); font-size: 1.1rem; font-weight: 400; letter-spacing: -0.02em;">Carlos Eduardo Ravello Joo</strong>', content)
    
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Updated {f}")
