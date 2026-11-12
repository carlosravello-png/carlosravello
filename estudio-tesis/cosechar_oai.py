#!/usr/bin/env python
"""
Estudio 3 (corpus de tesis). Paso 1: cosecha de METADATOS por OAI-PMH. No descarga ningún PDF.

Recorre los repositorios institucionales listados en REPOS con verb=ListRecords y
metadataPrefix=dim, y de cada registro guarda solo campos no personales:
  identificador OAI (handle), fecha OAI, si está borrado, dc.date.issued, dc.type,
  dc.rights, dc.format, thesis.degree.discipline, thesis.degree.name,
  renati.level, renati.type, renati.discipline.
Descarta en el acto nombres, DNI, ORCID, jurados, títulos y resúmenes: nunca se escriben a disco.

Salida, en la carpeta cosecha/:
  <repo>.jsonl          un registro por línea, en el orden en que lo entrega el servidor
  <repo>.log            una línea por página: fecha, n.º de registros, SHA-256 de los bytes recibidos
  manifiesto.txt        SHA-256 de cada .jsonl terminado (lo verifica contar.py)

Cortesía con los servidores: pausa entre peticiones de al menos SEGUNDOS_ENTRE_PETICIONES, que
se alarga a la par si el servidor responde lento; respeta Retry-After en 429/503; reintentos con
espera creciente; User-Agent con el correo de contacto, que hay que indicar al ejecutar.

Topes de tiempo (reloj del sistema, no estimaciones):
  - TOPE_TOTAL_HORAS para toda la corrida; al cumplirse se detiene limpio.
  - TOPE_REPO_HORAS por repositorio; al cumplirse lo pausa y pasa al siguiente.
  - Si una página falla todos los reintentos, ese repositorio se aparta en esta corrida.
En los tres casos queda guardado dónde iba: al volver a ejecutar, continúa desde ahí.
Al final imprime el estado de cada repositorio: terminado, pausado o apartado.

Uso:
  python cosechar_oai.py --correo tu@correo.com                (todos los repositorios)
  python cosechar_oai.py --correo tu@correo.com --solo UNT     (uno solo, para probar)
  python cosechar_oai.py --correo tu@correo.com --horas 10     (otro tope total)

Puntos de acceso verificados en vivo el 12-nov-2026.
"""
import argparse
import collections
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPOS = {
    "UCV": "https://repositorio.ucv.edu.pe/oai/request",
    "UNT": "https://repositorio.unitru.edu.pe/server/oai/request",
    "UNMSM": "https://cybertesis.unmsm.edu.pe/backend/oai/request",
    "USMP": "https://repositorio.usmp.edu.pe/backend/oai/request",
    "UPN": "https://repositorio.upn.edu.pe/backend/oai/request",
    "UPC": "https://repositorioacademico.upc.edu.pe/oai/request",
    "PUCP": "https://tesis.pucp.edu.pe/oai/request",
    "UNI": "https://repositorio.uni.edu.pe/server/oai/request",
}

SEGUNDOS_ENTRE_PETICIONES = 1.5   # pausa mínima; si el servidor tarda más, la pausa iguala su tiempo
PAUSA_MAXIMA = 30                 # segundos
REINTENTOS = 5
TIMEOUT = 120                     # segundos por petición
RETRY_AFTER_MAXIMO = 900          # no esperar más de 15 min aunque el servidor pida más
TOPE_TOTAL_HORAS = 36
TOPE_REPO_HORAS = 8


class Apartar(Exception):
    """El repositorio no responde bien: se aparta en esta corrida, con el avance guardado."""


def hms(seg):
    seg = int(seg)
    return f"{seg // 3600}:{seg % 3600 // 60:02d}:{seg % 60:02d}"

NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dim": "http://www.dspace.org/xmlns/dspace/dim",
}

# (mdschema, element, qualifier) -> nombre de campo de salida
CAMPOS = {
    ("dc", "date", "issued"): "fecha_emision",
    ("dc", "type", None): "dc_type",
    ("dc", "rights", None): "derechos",
    ("dc", "format", None): "formato",
    ("thesis", "degree", "discipline"): "disciplina",
    ("thesis", "degree", "name"): "grado",
    ("renati", "level", None): "renati_nivel",
    ("renati", "type", None): "renati_tipo",
    ("renati", "discipline", None): "renati_disciplina",
}


def pedir(url, correo):
    """Devuelve (bytes, raíz XML, segundos que tardó). Reintenta errores de red, 429/503 y XML cortado."""
    ua = f"RavelloJoo-estudio-tesis/1.0 (investigacion academica; mailto:{correo})"
    espera = 5
    for intento in range(1, REINTENTOS + 1):
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                crudo = r.read()
            return crudo, ET.fromstring(crudo), time.monotonic() - t0
        except urllib.error.HTTPError as e:
            pausa = espera
            if e.code in (429, 503):
                ra = e.headers.get("Retry-After", "")
                if ra.isdigit():
                    pausa = min(int(ra), RETRY_AFTER_MAXIMO)
            print(f"    reintento {intento}/{REINTENTOS}: HTTP {e.code}; espero {pausa} s", flush=True)
        except (urllib.error.URLError, TimeoutError, ConnectionError, ET.ParseError, OSError) as e:
            pausa = espera
            print(f"    reintento {intento}/{REINTENTOS}: {type(e).__name__}: {e}; espero {pausa} s", flush=True)
        time.sleep(pausa)
        espera *= 2
    raise Apartar(f"{REINTENTOS} fallos seguidos")


def extraer(registro):
    cab = registro.find("oai:header", NS)
    fila = {
        "id": cab.findtext("oai:identifier", default="", namespaces=NS),
        "fecha_oai": cab.findtext("oai:datestamp", default="", namespaces=NS),
        "borrado": cab.get("status") == "deleted",
    }
    for v in CAMPOS.values():
        fila[v] = []
    dim = registro.find("oai:metadata/dim:dim", NS)
    if dim is not None:
        for f in dim.findall("dim:field", NS):
            clave = (f.get("mdschema"), f.get("element"), f.get("qualifier"))
            if clave in CAMPOS and f.text:
                fila[CAMPOS[clave]].append(f.text.strip())
    return fila


def cosechar(nombre, base, correo, carpeta, fin_total, inicio_total):
    """Devuelve 'terminado', 'ya terminado', 'pausado (tope por repositorio)' o 'pausado (tope total)'."""
    destino = os.path.join(carpeta, f"{nombre}.jsonl")
    log = os.path.join(carpeta, f"{nombre}.log")
    control = os.path.join(carpeta, f"{nombre}.reanudar")
    hecho = os.path.join(carpeta, f"{nombre}.hecho")
    if os.path.exists(hecho):
        print(f"{nombre}: ya terminado, se omite.")
        return "ya terminado"

    if os.path.exists(control):
        with open(control, encoding="utf-8") as fh:
            estado = json.load(fh)
        url = base + "?" + urllib.parse.urlencode({"verb": "ListRecords", "resumptionToken": estado["token"]})
        pagina = estado["pagina"]
        # Si el corte ocurrió a mitad de una página, se descarta lo escrito después del último punto seguro.
        for ruta, clave in ((destino, "bytes_jsonl"), (log, "bytes_log")):
            with open(ruta, "r+b") as fh:
                fh.truncate(estado[clave])
        print(f"{nombre}: reanudando en la página {pagina + 1}")
    else:
        for p in (destino, log):
            if os.path.exists(p):
                os.remove(p)
        url = base + "?" + urllib.parse.urlencode({"verb": "ListRecords", "metadataPrefix": "dim"})
        pagina = 0

    inicio = time.monotonic()
    fin_repo = min(inicio + TOPE_REPO_HORAS * 3600, fin_total)
    duraciones = collections.deque(maxlen=10)   # segundos por página (petición + pausa), para estimar
    total_paginas = None
    while url:
        ahora = time.monotonic()
        if ahora >= fin_total:
            return "pausado (tope total)"
        if ahora >= fin_repo:
            return "pausado (tope por repositorio)"
        t_pag = time.monotonic()
        crudo, raiz, tardo = pedir(url, correo)
        huella = hashlib.sha256(crudo).hexdigest()
        error = raiz.find("oai:error", NS)
        if error is not None:
            raise Apartar(f"error OAI {error.get('code')}: {error.text}")
        lista = raiz.find("oai:ListRecords", NS)
        registros = lista.findall("oai:record", NS)
        with open(destino, "a", encoding="utf-8", newline="\n") as out:
            for reg in registros:
                out.write(json.dumps(extraer(reg), ensure_ascii=False, sort_keys=True) + "\n")
        pagina += 1
        token_el = lista.find("oai:resumptionToken", NS)
        token = (token_el.text or "").strip() if token_el is not None else ""
        total = token_el.get("completeListSize", "?") if token_el is not None else "?"
        with open(log, "a", encoding="utf-8", newline="\n") as lg:
            lg.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\tpagina={pagina}\tregistros={len(registros)}\t"
                     f"total_declarado={total}\tsha256={huella}\n")
        if total_paginas is None and str(total).isdigit() and registros:
            total_paginas = -(-int(total) // len(registros))
        if token:
            with open(control, "w", encoding="utf-8") as fh:
                json.dump({"token": token, "pagina": pagina,
                           "bytes_jsonl": os.path.getsize(destino), "bytes_log": os.path.getsize(log)}, fh)
            url = base + "?" + urllib.parse.urlencode({"verb": "ListRecords", "resumptionToken": token})
            time.sleep(min(max(SEGUNDOS_ENTRE_PETICIONES, tardo), PAUSA_MAXIMA))
        else:
            url = None
        duraciones.append(time.monotonic() - t_pag)
        if total_paginas:
            resto = max(total_paginas - pagina, 0) * sum(duraciones) / len(duraciones)
            avance = f"pág {pagina}/{total_paginas} ({100 * pagina / total_paginas:.1f}%) · faltan ≈ {hms(resto)}"
        else:
            avance = f"pág {pagina} (total no declarado)"
        print(f"  {nombre}  {avance} · respuesta {tardo:.1f} s · repo {hms(time.monotonic() - inicio)}"
              f" · total {hms(time.monotonic() - inicio_total)}", flush=True)

    if os.path.exists(control):
        os.remove(control)
    with open(destino, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    with open(os.path.join(carpeta, "manifiesto.txt"), "a", encoding="utf-8", newline="\n") as mf:
        mf.write(f"{nombre}.jsonl\t{sha}\t{time.strftime('%Y-%m-%d')}\n")
    open(hecho, "w").close()
    print(f"{nombre}: terminado. SHA-256 {sha}")
    return "terminado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--correo", required=True, help="correo de contacto para el User-Agent")
    ap.add_argument("--solo", help="cosechar un solo repositorio, p. ej. UNT")
    ap.add_argument("--carpeta", default="cosecha")
    ap.add_argument("--horas", type=float, default=TOPE_TOTAL_HORAS, help="tope total de la corrida")
    a = ap.parse_args()
    if "@" not in a.correo:
        sys.exit("Indica un correo válido con --correo")
    os.makedirs(a.carpeta, exist_ok=True)
    objetivo = {a.solo: REPOS[a.solo]} if a.solo else REPOS
    inicio_total = time.monotonic()
    fin_total = inicio_total + a.horas * 3600
    print(f"Inicio {time.strftime('%Y-%m-%d %H:%M')}. Tope total {a.horas:g} h; "
          f"tope por repositorio {TOPE_REPO_HORAS} h.")
    estados = {}
    for nombre, base in objetivo.items():
        if time.monotonic() >= fin_total:
            estados[nombre] = "no iniciado (tope total)"
            continue
        print(f"== {nombre} ({base})")
        try:
            estados[nombre] = cosechar(nombre, base, a.correo, a.carpeta, fin_total, inicio_total)
        except Apartar as e:
            estados[nombre] = f"apartado: {e}"
        print(f"{nombre}: {estados[nombre]}", flush=True)
    print(f"\nFin {time.strftime('%Y-%m-%d %H:%M')} tras {hms(time.monotonic() - inicio_total)}. Estado:")
    for nombre, est in estados.items():
        print(f"  {nombre}\t{est}")
    if any(not e.endswith("terminado") for e in estados.values()):
        print("Vuelve a ejecutar el mismo comando para continuar los no terminados.")


if __name__ == "__main__":
    main()
