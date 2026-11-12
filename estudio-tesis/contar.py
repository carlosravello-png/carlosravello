#!/usr/bin/env python
"""
Estudio 3 (corpus de tesis). Paso 2: conteo desde la cosecha. No hace peticiones a la red.

Lee cosecha/*.jsonl, comprueba cada fichero contra cosecha/manifiesto.txt y se detiene si
un SHA-256 no coincide. Un repositorio sin terminar no se cuenta y el resumen lo dice. Cuenta tesis por universidad, carrera, año y nivel, con el acceso al PDF.

Reglas (todas visibles para auditarlas):
  - Es tesis si renati_tipo contiene "#tesis" o, si falta, si dc_type contiene "Thesis".
  - Año: los 4 primeros dígitos de fecha_emision (dc.date.issued). No se usa la fecha OAI.
  - Carrera: a partir de "disciplina" (thesis.degree.discipline) con las reglas de CARRERAS.
    Lo que no encaja va a "Otra". disciplinas.csv lista cada texto de disciplina con su
    carrera asignada, para revisar la clasificación a mano.
  - Acceso: abierto si "derechos" contiene openAccess o COAR c_abf2; embargado si embargoedAccess
    o c_f1cf; restringido si restrictedAccess, closedAccess, c_16ec o c_14cb; si no, sin_dato.
  - Nivel: el fragmento tras "#" en renati_nivel (p. ej., tituloProfesional, maestro, doctor).
    Si renati_nivel falta, respaldo con dc_type: masterThesis o COAR c_bdcc -> maestro,
    doctoralThesis o c_db06 -> doctor, bachelorThesis o c_7a1f -> pregrado_sin_detalle;
    si tampoco, sin_dato. El resumen dice cuántas tesis tomaron el nivel del respaldo.
  - Posgrado = maestro + doctor. La segunda especialidad se cuenta aparte, no como posgrado.

Salidas (saltos de línea "\n", idénticas byte a byte en cualquier entorno):
  conteo.csv        universidad, carrera, año, nivel, total, abierto, embargado, restringido, sin_dato
  disciplinas.csv   universidad, disciplina, carrera asignada, número de tesis
  resumen_conteo.txt

Uso: python contar.py            (lee la carpeta cosecha/)
     python contar.py --desde 2018 --hasta 2026
"""
import argparse
import collections
import glob
import hashlib
import json
import os
import sys
import unicodedata

CARRERAS = [  # (carrera, fragmentos a buscar en la disciplina normalizada), en orden de prioridad
    ("Psicologia", ["psicolog"]),
    ("Derecho", ["derecho", "abogad", "ciencias juridicas", "ciencia juridica"]),
    ("Salud", ["medicina", "medico", "enfermer", "obstetric", "odontolog", "estomatolog", "tecnologia medica",
               "nutricion", "farmac", "salud", "terapia", "laboratorio clinico", "radiolog"]),
    ("Ingenieria", ["ingenier"]),
]


def normalizar(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c)).strip()


def carrera_de(disciplinas):
    texto = " | ".join(normalizar(d) for d in disciplinas)
    if not texto:
        return "Sin disciplina"
    for nombre, claves in CARRERAS:
        if any(k in texto for k in claves):
            return nombre
    return "Otra"


# Vocabulario COAR (purl.org/coar/resource_type): c_46ec tesis, c_7a1f tesis de pregrado,
# c_bdcc tesis de maestría, c_db06 tesis doctoral.
COAR_TESIS = ("c_46ec", "c_7a1f", "c_bdcc", "c_db06")


def es_tesis(f):
    if f["renati_tipo"]:
        return any("#tesis" in v for v in f["renati_tipo"])
    return any("thesis" in v.lower() or v.rstrip("/").endswith(COAR_TESIS) for v in f["dc_type"])


# Derechos: vocabulario info:eu-repo y su equivalente COAR (purl.org/coar/access_right):
# c_abf2 abierto, c_f1cf embargado, c_16ec restringido, c_14cb solo metadatos.
def acceso(derechos):
    d = " ".join(derechos)
    if "openAccess" in d or "c_abf2" in d:
        return "abierto"
    if "embargoedAccess" in d or "c_f1cf" in d:
        return "embargado"
    if "restrictedAccess" in d or "closedAccess" in d or "c_16ec" in d or "c_14cb" in d:
        return "restringido"
    return "sin_dato"


def anio(fechas):
    for f in fechas:
        if len(f) >= 4 and f[:4].isdigit():
            return int(f[:4])
    return None


RESPALDO_NIVEL = [("doctoralthesis", "doctor"), ("c_db06", "doctor"),
                  ("masterthesis", "maestro"), ("c_bdcc", "maestro"),
                  ("bachelorthesis", "pregrado_sin_detalle"), ("c_7a1f", "pregrado_sin_detalle")]


def nivel(f):
    """Devuelve (nivel, origen) con origen 'renati', 'dc_type' o 'ninguno'."""
    for n in f["renati_nivel"]:
        if "#" in n:
            return n.rsplit("#", 1)[1], "renati"
    tipos = " ".join(f["dc_type"]).lower()
    for clave, nv in RESPALDO_NIVEL:
        if clave in tipos:
            return nv, "dc_type"
    return "sin_dato", "ninguno"


def grupo(nv):
    if nv in ("maestro", "doctor"):
        return nv
    if "segunda" in nv.lower():
        return "segunda_esp"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default="cosecha")
    ap.add_argument("--desde", type=int, default=2018)
    ap.add_argument("--hasta", type=int, default=2026)
    a = ap.parse_args()

    manifiesto = {}
    ruta_m = os.path.join(a.carpeta, "manifiesto.txt")
    if not os.path.exists(ruta_m):
        sys.exit("ALTO: falta cosecha/manifiesto.txt. ¿Terminó la cosecha?")
    with open(ruta_m, encoding="utf-8") as fh:
        for linea in fh:
            nombre, sha, _ = linea.rstrip("\n").split("\t")
            manifiesto[nombre] = sha

    conteo = collections.Counter()
    disciplinas = collections.Counter()
    resumen = []
    for ruta in sorted(glob.glob(os.path.join(a.carpeta, "*.jsonl"))):
        nombre = os.path.basename(ruta)
        with open(ruta, "rb") as fh:
            crudo = fh.read()
        sha = hashlib.sha256(crudo).hexdigest()
        if nombre not in manifiesto:
            aviso = f"{nombre[:-6]}: SIN CONTAR, cosecha no terminada (no está en el manifiesto)"
            print(aviso)
            resumen.append(aviso)
            continue
        if manifiesto[nombre] != sha:
            sys.exit(f"ALTO: {nombre} no coincide con el manifiesto.\n  manifiesto: {manifiesto.get(nombre)}\n  fichero:    {sha}")
        uni = nombre[:-len(".jsonl")]
        n = borrados = no_tesis = sin_anio = fuera_rango = respaldo = sin_nivel = 0
        for linea in crudo.decode("utf-8").splitlines():
            f = json.loads(linea)
            n += 1
            if f["borrado"]:
                borrados += 1
                continue
            if not es_tesis(f):
                no_tesis += 1
                continue
            y = anio(f["fecha_emision"])
            if y is None:
                sin_anio += 1
                continue
            if not (a.desde <= y <= a.hasta):
                fuera_rango += 1
                continue
            c = carrera_de(f["disciplina"])
            nv, origen = nivel(f)
            respaldo += origen == "dc_type"
            sin_nivel += origen == "ninguno"
            conteo[(uni, c, y, nv, acceso(f["derechos"]))] += 1
            disciplinas[(uni, " | ".join(f["disciplina"]) or "(vacía)", c)] += 1
        resumen.append(f"{uni}: {n} registros; borrados {borrados}; no tesis {no_tesis}; "
                       f"tesis sin año {sin_anio}; tesis fuera de {a.desde}-{a.hasta} {fuera_rango}; "
                       f"nivel por respaldo dc_type {respaldo}; nivel sin dato {sin_nivel}; "
                       f"SHA-256 {sha}")

    celdas = collections.defaultdict(collections.Counter)
    for (uni, c, y, nv, ac), k in conteo.items():
        celdas[(uni, c, y, nv)][ac] += k
    cols = ["abierto", "embargado", "restringido", "sin_dato"]
    with open("conteo.csv", "w", encoding="utf-8", newline="\n") as out:
        out.write("universidad,carrera,anio,nivel,total," + ",".join(cols) + "\n")
        for clave in sorted(celdas):
            v = celdas[clave]
            out.write(",".join(str(x) for x in clave) + f",{sum(v.values())}," +
                      ",".join(str(v[c]) for c in cols) + "\n")
    with open("disciplinas.csv", "w", encoding="utf-8", newline="\n") as out:
        out.write("universidad,disciplina,carrera_asignada,tesis\n")
        for (uni, d, c), k in sorted(disciplinas.items()):
            d = d.replace('"', "'")
            out.write(f'{uni},"{d}",{c},{k}\n')

    total = collections.Counter()
    for (uni, c, y, nv), v in celdas.items():
        total[(uni, c)] += sum(v.values())
    resumen.append("")
    resumen.append(f"Tesis {a.desde}-{a.hasta} por universidad y carrera (todos los niveles):")
    for (uni, c) in sorted(total):
        resumen.append(f"  {uni}\t{c}\t{total[(uni, c)]}")
    pos = collections.defaultdict(collections.Counter)
    pos_anio = collections.defaultdict(collections.Counter)
    for (uni, c, y, nv), v in celdas.items():
        g = grupo(nv)
        if g is None:
            continue
        k = sum(v.values())
        pos[(uni, c)][g] += k
        if g != "segunda_esp":
            pos[(uni, c)]["abierto"] += v["abierto"]
            pos_anio[uni][y] += k
    resumen.append("")
    resumen.append(f"Posgrado {a.desde}-{a.hasta} por universidad y carrera "
                   "(maestro, doctor, de ellas con PDF abierto; segunda especialidad aparte):")
    resumen.append("  universidad\tcarrera\tmaestro\tdoctor\tabierto\tsegunda_esp")
    for (uni, c) in sorted(pos):
        v = pos[(uni, c)]
        resumen.append(f"  {uni}\t{c}\t{v['maestro']}\t{v['doctor']}\t{v['abierto']}\t{v['segunda_esp']}")
    resumen.append("")
    resumen.append("Posgrado (maestro + doctor) por universidad y año:")
    for uni in sorted(pos_anio):
        resumen.append(f"  {uni}\t" + "\t".join(f"{y}:{pos_anio[uni][y]}" for y in sorted(pos_anio[uni])))
    with open("resumen_conteo.txt", "w", encoding="utf-8", newline="\n") as out:
        out.write("\n".join(resumen) + "\n")
    print("\n".join(resumen))


if __name__ == "__main__":
    main()
