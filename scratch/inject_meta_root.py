import os
import re

base_dir = r"c:\Users\RAVELLO CAMACHO\Documents\GitHub\carlosravello"

path = os.path.join(base_dir, "metacognition-2-0.html")
with open(path, 'r', encoding='utf-8') as file:
    content = file.read()

svg_flavell = """
            <figure class="paper-fig" id="fig-1">
                <a href="/svg-metacognicion-2.0/flavell-1979-cognitive-monitoring-model-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 1 in full size">
                    <img src="/svg-metacognicion-2.0/flavell-1979-cognitive-monitoring-model-dark.svg"
                         alt="Flavell's model of cognitive monitoring (1979): four classes of phenomena — metacognitive knowledge, metacognitive experiences, goals, and actions — in dynamic interaction."
                         width="1280" height="760" loading="lazy">
                </a>
                <figcaption>Fig. 1 — Flavell, J. H. (1979). Metacognition and cognitive monitoring. <cite>American Psychologist, 34</cite>(10), 906–911. · <a href="https://doi.org/10.1037/0003-066X.34.10.906" target="_blank" rel="noopener">doi:10.1037/0003-066X.34.10.906</a> · <a href="https://commons.wikimedia.org/wiki/File:Flavell-1979-cognitive-monitoring-model.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>
"""

svg_kosinski = """
            <figure class="paper-fig" id="fig-3">
                <a href="/svg-metacognicion-2.0/kosinski-2013-private-traits-digital-footprints-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 3 in full size">
                    <img src="/svg-metacognicion-2.0/kosinski-2013-private-traits-digital-footprints-dark.svg"
                         alt="Personal attributes predictable from digital footprints (Kosinski et al., 2013): AUC 0.95 for ethnicity, Pearson r up to 0.43 for Big Five personality traits."
                         width="1280" height="820" loading="lazy">
                </a>
                <figcaption>Fig. 3 — Kosinski, M., Stillwell, D., &amp; Graepel, T. (2013). Private traits and attributes are predictable from digital records of human behavior. <cite>PNAS, 110</cite>(15), 5802–5805. · <a href="https://doi.org/10.1073/pnas.1218772110" target="_blank" rel="noopener">doi:10.1073/pnas.1218772110</a> · <a href="https://commons.wikimedia.org/wiki/File:Kosinski-2013-private-traits-digital-footprints.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>
"""

if 'id="fig-1"' not in content:
    content = re.sub(r'(<p>Metacognition has a history.*?in certain niches.</p>)', r'\1\n' + svg_flavell, content, flags=re.DOTALL)
    content = re.sub(r'(<p>But in the era where we let AIs think.*?you give me this, I give you that.</em></p>)', r'\1\n' + svg_kosinski, content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print("Injected EN root metacognition")
