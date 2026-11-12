# Estudio 3: corpus de tesis de universidades peruanas (paso 1, metadatos)

Carlos Eduardo Ravello Joo · ORCID 0009-0007-5631-7436 · cosecha del 12-nov-2026

Esta carpeta guarda la cosecha de **metadatos** (no PDF) de los repositorios institucionales de ocho universidades por OAI-PMH, y el conteo que se obtiene de ella. Sirve para decidir la muestra del estudio antes de prerregistrarlo. Todavía no se ha abierto ninguna tesis.

## Qué hay
| Archivo | Qué es |
|---|---|
| `cosechar_oai.py` | Cosecha OAI-PMH (`ListRecords`, `metadataPrefix=dim`). Guarda solo campos no personales. |
| `descomprimir.py` | Descomprime `cosecha/*.jsonl.gz` y comprueba cada archivo contra el manifiesto. |
| `contar.py` | Cuenta tesis por universidad, carrera, año, nivel y acceso. No usa la red. |
| `cosecha/*.jsonl.gz` | Cosecha comprimida, un archivo por universidad (gzip determinista, `-n -9`). |
| `cosecha/manifiesto.txt` | SHA-256 de cada `.jsonl` tal como salió de la cosecha. |
| `cosecha/SHA256SUMS-gz.txt` | SHA-256 de cada `.jsonl.gz`. |
| `cosecha/*.log` | Una línea por página: hora, registros, total declarado y SHA-256 de la respuesta del servidor. |
| `resumen_conteo.txt`, `conteo.csv`, `disciplinas.csv` | Salidas de `contar.py`. |

## Cosecha
| Universidad | Punto OAI | Registros (= total declarado) |
|---|---|---|
| UCV | repositorio.ucv.edu.pe/oai/request | 189.197 |
| UPC | repositorioacademico.upc.edu.pe/oai/request | 72.106 |
| UPN | repositorio.upn.edu.pe/backend/oai/request | 38.889 |
| PUCP | tesis.pucp.edu.pe/oai/request | 32.080 |
| UNMSM | cybertesis.unmsm.edu.pe/backend/oai/request | 31.054 |
| UNI | repositorio.uni.edu.pe/server/oai/request | 29.047 |
| UNT | repositorio.unitru.edu.pe/server/oai/request | 26.373 |
| USMP | repositorio.usmp.edu.pe/backend/oai/request | 21.719 |

En total son 440.465 registros. La cosecha corrió el 12-nov-2026 entre las 10:02 y las 13:23 (hora de Perú), sin cortes.

**Privacidad:** el formato `dim` incluye nombres, DNI, asesores, jurados y títulos. El script los descarta antes de escribir a disco. Por registro se guardan solo estos campos: identificador OAI, fechas, si está borrado, tipo, derechos, formato, disciplina, grado y los campos RENATI de nivel, tipo y disciplina. Los resultados se publican agregados por universidad; nunca por tesis ni por autor.

## Reproducir el conteo
Requiere Python 3 y solo la biblioteca estándar.
```
python descomprimir.py
python contar.py
```
`resumen_conteo.txt`, `conteo.csv` y `disciplinas.csv` deben salir idénticos byte a byte a los de esta carpeta. Comprobado en dos entornos, Windows (Miniconda) y Linux, el 12-nov-2026.

La cosecha en sí no es reproducible, porque los repositorios cambian con el tiempo. Por eso queda guardada con fecha y huellas. Para volver a cosechar: `python cosechar_oai.py --correo TU_CORREO`.

## Reglas del conteo
Están en el encabezado de `contar.py`. En resumen:
- **Es tesis:** RENATI `type#tesis` o, si falta, `dc.type` de tesis, en el vocabulario info:eu-repo o en COAR (`c_46ec`, `c_7a1f`, `c_bdcc`, `c_db06`).
- **Año:** `dc.date.issued`.
- **Nivel:** RENATI `level`, con respaldo en `dc.type`.
- **Acceso:** info:eu-repo o COAR (`c_abf2`, `c_f1cf`, `c_16ec`, `c_14cb`).
- **Carrera:** se asigna por palabras clave sobre la disciplina; `disciplinas.csv` permite auditar la asignación.

Las carreras y la muestra se fijan en el prerregistro, todavía pendiente.
