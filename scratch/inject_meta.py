import os
import re

base_dir = r"c:\Users\RAVELLO CAMACHO\Documents\GitHub\carlosravello"

path = os.path.join(base_dir, "research/metacognition-2-0.html")
with open(path, 'r', encoding='utf-8') as file:
    content = file.read()

svgs = """
            <div class="section-label">Figures</div>

            <figure class="paper-fig" id="fig-1">
                <a href="/svg-metacognicion-2.0/flavell-1979-cognitive-monitoring-model-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 1 in full size">
                    <img src="/svg-metacognicion-2.0/flavell-1979-cognitive-monitoring-model-dark.svg"
                         alt="Flavell's model of cognitive monitoring (1979): four classes of phenomena — metacognitive knowledge, metacognitive experiences, goals, and actions — in dynamic interaction."
                         width="1280" height="760" loading="lazy">
                </a>
                <figcaption><strong>Fig. 1.</strong> Flavell, J. H. (1979). Metacognition and cognitive monitoring: A new area of cognitive-developmental inquiry. <cite>American Psychologist, 34</cite>(10), 906–911. <a href="https://doi.org/10.1037/0003-066X.34.10.906" target="_blank" rel="noopener">doi:10.1037/0003-066X.34.10.906</a> · <a href="https://commons.wikimedia.org/wiki/File:Flavell-1979-cognitive-monitoring-model.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>

            <figure class="paper-fig" id="fig-2">
                <a href="/svg-metacognicion-2.0/friston-2010-free-energy-principle-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 2 in full size">
                    <img src="/svg-metacognicion-2.0/friston-2010-free-energy-principle-dark.svg"
                         alt="Friston's Free-Energy Principle (2010): two paths to minimize surprise — perception (updating beliefs) and action (modifying the world)."
                         width="1280" height="760" loading="lazy">
                </a>
                <figcaption><strong>Fig. 2.</strong> Friston, K. (2010). The free-energy principle: a unified brain theory? <cite>Nature Reviews Neuroscience, 11</cite>(2), 127–138. <a href="https://doi.org/10.1038/nrn2787" target="_blank" rel="noopener">doi:10.1038/nrn2787</a> · <a href="https://commons.wikimedia.org/wiki/File:Friston-2010-free-energy-principle.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>

            <figure class="paper-fig" id="fig-3">
                <a href="/svg-metacognicion-2.0/kosinski-2013-private-traits-digital-footprints-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 3 in full size">
                    <img src="/svg-metacognicion-2.0/kosinski-2013-private-traits-digital-footprints-dark.svg"
                         alt="Personal attributes predictable from digital footprints (Kosinski et al., 2013): AUC 0.95 for ethnicity, Pearson r up to 0.43 for Big Five personality traits."
                         width="1280" height="820" loading="lazy">
                </a>
                <figcaption><strong>Fig. 3.</strong> Kosinski, M., Stillwell, D., &amp; Graepel, T. (2013). Private traits and attributes are predictable from digital records of human behavior. <cite>PNAS, 110</cite>(15), 5802–5805. <a href="https://doi.org/10.1073/pnas.1218772110" target="_blank" rel="noopener">doi:10.1073/pnas.1218772110</a> · <a href="https://commons.wikimedia.org/wiki/File:Kosinski-2013-private-traits-digital-footprints.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>

            <figure class="paper-fig" id="fig-4">
                <a href="/svg-metacognicion-2.0/ashby-1956-law-of-requisite-variety-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="View Figure 4 in full size">
                    <img src="/svg-metacognicion-2.0/ashby-1956-law-of-requisite-variety-dark.svg"
                         alt="Ashby's Law of Requisite Variety (1956): V(R) ≥ V(D). A regulator can only absorb the variety of perturbations if it possesses equal or greater variety."
                         width="1280" height="760" loading="lazy">
                </a>
                <figcaption><strong>Fig. 4.</strong> Ashby, W. R. (1956). <cite>An Introduction to Cybernetics</cite> (§11/7). Chapman &amp; Hall. <a href="https://archive.org/details/introductiontocy0000ashb" target="_blank" rel="noopener">archive.org</a> · <a href="https://commons.wikimedia.org/wiki/File:Ashby-1956-law-of-requisite-variety.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
            </figure>
"""

if 'id="fig-1"' not in content:
    content = content.replace('<div class="section-label">Full text</div>', svgs + '\n            <div class="section-label">Full text</div>')

with open(path, 'w', encoding='utf-8') as file:
    file.write(content)
print("Injected EN acad metacognition")
