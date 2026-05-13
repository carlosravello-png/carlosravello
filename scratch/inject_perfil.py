import os
import re

base_dir = r"c:\Users\RAVELLO CAMACHO\Documents\GitHub\carlosravello"

# Inject into ES files
es_files = [
    "el-perfil-que-no-escribiste.html",
    "produccion-academica/el-perfil-que-no-escribiste.html"
]

svg_brin = """
        <figure class="paper-fig" id="fig-1">
            <a href="/svg-el-perfil-que-no-escribiste/brin-page-1998-pagerank-algorithm-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="Ver figura 1 en tamaño completo">
                <img src="/svg-el-perfil-que-no-escribiste/brin-page-1998-pagerank-algorithm-dark.svg" alt="Algoritmo PageRank de Brin y Page (1998): propagación de autoridad en un grafo dirigido donde cada nodo transfiere valor a sus vecinos." width="1280" height="760" loading="lazy">
            </a>
            <figcaption>Fig. 1 — Brin, S., &amp; Page, L. (1998). The anatomy of a large-scale hypertextual Web search engine. <cite>Computer Networks and ISDN Systems, 30</cite>(1-7), 107-117. · <a href="https://doi.org/10.1016/S0169-7552(98)00110-X" target="_blank" rel="noopener">doi:10.1016/S0169-7552(98)00110-X</a> · <a href="https://commons.wikimedia.org/wiki/File:Brin-page-1998-pagerank-algorithm.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
        </figure>
"""

svg_node2vec = """
        <figure class="paper-fig" id="fig-2">
            <a href="/svg-el-perfil-que-no-escribiste/grover-leskovec-2016-node2vec-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="Ver figura 2 en tamaño completo">
                <img src="/svg-el-perfil-que-no-escribiste/grover-leskovec-2016-node2vec-dark.svg" alt="Arquitectura Node2Vec de Grover y Leskovec (2016): aprendizaje de representaciones continuas para nodos en redes multidimensionales." width="1280" height="760" loading="lazy">
            </a>
            <figcaption>Fig. 2 — Grover, A., &amp; Leskovec, J. (2016). node2vec: Scalable feature learning for networks. <cite>KDD '16</cite>, 855-864. · <a href="https://doi.org/10.1145/2939672.2939754" target="_blank" rel="noopener">doi:10.1145/2939672.2939754</a> · <a href="https://commons.wikimedia.org/wiki/File:Grover-leskovec-2016-node2vec.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
        </figure>
"""

svg_iris = """
        <figure class="paper-fig" id="fig-3">
            <a href="/svg-el-perfil-que-no-escribiste/iris-recognition-biometric-pipeline-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="Ver figura 3 en tamaño completo">
                <img src="/svg-el-perfil-que-no-escribiste/iris-recognition-biometric-pipeline-dark.svg" alt="Pipeline biométrico de reconocimiento de iris: desde la adquisición de la imagen hasta la extracción de características y generación del IrisCode." width="1280" height="760" loading="lazy">
            </a>
            <figcaption>Fig. 3 — Daugman, J. (2004). How iris recognition works. <cite>IEEE Transactions on Circuits and Systems for Video Technology, 14</cite>(1), 21-30. · <a href="https://doi.org/10.1109/TCSVT.2003.818350" target="_blank" rel="noopener">doi:10.1109/TCSVT.2003.818350</a> · <a href="https://commons.wikimedia.org/wiki/File:Iris-recognition-biometric-pipeline.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
        </figure>
"""

svg_cambridge = """
        <figure class="paper-fig" id="fig-4">
            <a href="/svg-el-perfil-que-no-escribiste/cambridge-analytica-2018-data-extraction-cascade-dark.svg" target="_blank" rel="noopener" class="fig-zoom" aria-label="Ver figura 4 en tamaño completo">
                <img src="/svg-el-perfil-que-no-escribiste/cambridge-analytica-2018-data-extraction-cascade-dark.svg" alt="Cascada de extracción de datos de Cambridge Analytica (2018): propagación de recolección de perfiles psicográficos a través de grafos sociales de la plataforma." width="1280" height="760" loading="lazy">
            </a>
            <figcaption>Fig. 4 — Isaak, J., &amp; Hanna, M. J. (2018). User data privacy: Facebook, Cambridge Analytica, and privacy protection. <cite>Computer, 51</cite>(8), 56-59. · <a href="https://doi.org/10.1109/MC.2018.3191268" target="_blank" rel="noopener">doi:10.1109/MC.2018.3191268</a> · <a href="https://commons.wikimedia.org/wiki/File:Cambridge-analytica-2018-data-extraction-cascade.svg" target="_blank" rel="noopener">Wikimedia Commons (CC BY-SA 4.0)</a></figcaption>
        </figure>
"""

for f in es_files:
    path = os.path.join(base_dir, f)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'id="fig-1"' not in content:
        # Insert brin after formula-block
        content = re.sub(r'(<div class="formula-block">.*?</div>)', r'\1\n' + svg_brin, content, flags=re.DOTALL)
        # Insert node2vec after "En términos humanos..." paragraph
        content = re.sub(r'(<p>En términos humanos:.*?reposición tiene consecuencias medibles.</p>)', r'\1\n' + svg_node2vec, content, flags=re.DOTALL)
        # Insert iris after "El reconocimiento de iris ya opera..."
        content = re.sub(r'(<p>El <strong>reconocimiento de iris</strong> ya opera en aeropuertos.*?qué estaba cediendo.</p>)', r'\1\n' + svg_iris, content, flags=re.DOTALL)
        # Insert cambridge after "Cambridge Analytica construyó perfiles..."
        content = re.sub(r'(<p>No hace falta buscar lejos. <strong>Cambridge Analytica</strong> construyó perfiles.*?legal de ese momento.</p>)', r'\1\n' + svg_cambridge, content, flags=re.DOTALL)
        
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Injected ES in {f}")

# English files
en_files = [
    "the-profile-you-didnt-write.html",
    "research/the-profile-you-didnt-write.html"
]

svg_brin_en = svg_brin.replace("Fig. 1 —", "Fig. 1 —")
svg_node2vec_en = svg_node2vec.replace("Fig. 2 —", "Fig. 2 —")
svg_iris_en = svg_iris.replace("Fig. 3 —", "Fig. 3 —")
svg_cambridge_en = svg_cambridge.replace("Fig. 4 —", "Fig. 4 —")

for f in en_files:
    path = os.path.join(base_dir, f)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'id="fig-1"' not in content:
        # Insert brin after formula-block
        content = re.sub(r'(<div class="formula-block">.*?</div>)', r'\1\n' + svg_brin_en, content, flags=re.DOTALL)
        # Insert node2vec after "In human terms:" paragraph
        content = re.sub(r'(<p>In human terms:.*?repositioning has measurable consequences.</p>)', r'\1\n' + svg_node2vec_en, content, flags=re.DOTALL)
        # Insert iris after "Iris recognition is already operating..."
        content = re.sub(r'(<p><strong>Iris recognition</strong> is already operating in airports.*?they were giving away.</p>)', r'\1\n' + svg_iris_en, content, flags=re.DOTALL)
        # Insert cambridge after "Cambridge Analytica built..."
        content = re.sub(r'(<p>You don\'t have to look far. <strong>Cambridge Analytica</strong> built.*?legal framework of the time.</p>)', r'\1\n' + svg_cambridge_en, content, flags=re.DOTALL)
        
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Injected EN in {f}")
