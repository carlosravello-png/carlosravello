#!/usr/bin/env python
"""
Estudio 3 (corpus de tesis). Paso 0 para reproducir: descomprime la cosecha guardada.

Lee cosecha/*.jsonl.gz, escribe cosecha/*.jsonl y comprueba cada archivo contra
cosecha/manifiesto.txt (el SHA-256 que registró la cosecha original). Si alguno no coincide,
se detiene. Después basta con correr contar.py.

Solo usa la biblioteca estándar.
Uso: python descomprimir.py
"""
import glob
import gzip
import hashlib
import os
import sys

carpeta = "cosecha"
manifiesto = {}
with open(os.path.join(carpeta, "manifiesto.txt"), encoding="utf-8") as fh:
    for linea in fh:
        nombre, sha, _ = linea.rstrip("\n").split("\t")
        manifiesto[nombre] = sha

archivos = sorted(glob.glob(os.path.join(carpeta, "*.jsonl.gz")))
if not archivos:
    sys.exit("ALTO: no hay archivos .jsonl.gz en cosecha/")
for ruta in archivos:
    nombre = os.path.basename(ruta)[:-len(".gz")]
    with gzip.open(ruta, "rb") as fh:
        datos = fh.read()
    sha = hashlib.sha256(datos).hexdigest()
    if manifiesto.get(nombre) != sha:
        sys.exit(f"ALTO: {nombre} no coincide con el manifiesto.\n  manifiesto: {manifiesto.get(nombre)}\n  archivo:    {sha}")
    with open(os.path.join(carpeta, nombre), "wb") as out:
        out.write(datos)
    n = datos.count(b"\n")
    print(f"{nombre}: {n} registros, SHA-256 {sha} (coincide)")
print("Listo. Ahora: python contar.py")
