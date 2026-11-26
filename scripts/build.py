"""
build.py — Genera el dashboard (index.html) a partir del Excel del Comité.

Uso (desde la carpeta raíz del proyecto):
    python scripts/build.py                 -> crea index.html con nombres completos
    python scripts/build.py --anonimo       -> crea index_anonimo.html con códigos en vez de nombres

Requisito: pip install openpyxl
Los datos NO se modifican: solo se leen del Excel y se insertan en la plantilla.
"""

import argparse          # para leer opciones de la línea de comandos (--anonimo, --excel)
import base64            # para convertir el escudo en texto e incrustarlo dentro del HTML
import json              # para convertir los datos a texto JSON e insertarlos en el HTML
import re                # expresiones regulares: para encontrar la nota de DISCP en el texto
from pathlib import Path # para manejar rutas de archivos de forma segura en Mac, Windows o Linux

import openpyxl          # librería para leer archivos de Excel (.xlsx)

# Carpeta raíz del proyecto (la carpeta que contiene a /scripts)
RAIZ = Path(__file__).resolve().parent.parent

# Orden oficial de los grados; cada uno es una hoja del Excel
GRADOS = ["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "11-1"]

# Estudiantes promovidos por decisión del comité, además de los que cumplen el criterio
# de repechaje (este criterio se calcula en src/template.html, constante PRIO).
# Se escriben como (grado, nombre exacto del Excel).
PROMO_COMITE = [
    ("6-1", "ORTIZ CUERO BRITHANY SOFIA"),
    ("6-2", "GONZALEZ MALAGA HERNANDO"),
]


def leer_estudiantes(libro):
    """Recorre las hojas por grado y devuelve una lista de estudiantes (diccionarios)."""
    estudiantes = []                                   # aquí se acumulan todos los estudiantes
    for grado in GRADOS:                               # recorre cada hoja de grado
        hoja = libro[grado]                            # abre la hoja con el nombre del grado
        for fila in hoja.iter_rows(min_row=4, values_only=True):  # los datos empiezan en la fila 4
            if not fila[0]:                            # si la celda del nombre está vacía, se salta
                continue
            nombre, n_bajo, inasist, desemp, estado, perdidas, promedio = fila[:7]  # las 7 columnas
            lineas = perdidas.split("\n")              # la 1.ª línea son las áreas; la 2.ª, DISCP (si existe)
            areas = []                                 # lista de [código de área, valoración]
            for parte in lineas[0].split(";"):         # cada área viene separada por ";"
                codigo, valor = parte.rsplit(":", 1)   # separa "MATE: 2,8" en "MATE" y "2,8"
                areas.append([codigo.strip(), float(valor.strip().replace(",", "."))])  # coma -> punto decimal
            disc = None                                # DISCP se guarda aparte (no es área académica)
            for extra in lineas[1:]:                   # revisa las líneas adicionales
                m = re.search(r"DISCP:\s*([\d,]+)", extra)   # busca el número que sigue a "DISCP:"
                if m:
                    disc = float(m.group(1).replace(",", "."))
            estudiantes.append(dict(                   # guarda el estudiante con nombres cortos de campo
                g=grado, n=nombre, nb=n_bajo, i=inasist, d=desemp,
                e=estado, a=areas, disc=disc, p=promedio, raw=perdidas,
            ))
    return estudiantes


def leer_casos(libro):
    """Lee la hoja 'Casos 1 área' y devuelve los nombres listados (se detiene en la primera fila vacía)."""
    casos = []
    for fila in libro["Casos 1 área"].iter_rows(min_row=4, values_only=True):
        if not fila[0]:            # la tabla de casos termina en la primera fila vacía
            break
        casos.append(fila[1])      # la columna B tiene "Apellidos y Nombres"
    return casos


def verificar(estudiantes, libro):
    """Comprueba que los datos leídos cuadren con la hoja 'Resumen'. Detiene el proceso si no cuadran."""
    resumen = {}
    for fila in libro["Resumen"].iter_rows(min_row=5, max_row=14, values_only=True):
        resumen[fila[0]] = (fila[1], fila[2])          # grado -> (reprobados, áreas en bajo)
    for grado in GRADOS:
        grupo = [s for s in estudiantes if s["g"] == grado]           # estudiantes de ese grado
        calculado = (len(grupo), sum(s["nb"] for s in grupo))        # conteo propio
        assert calculado == tuple(resumen[grado]), f"{grado}: {calculado} ≠ Resumen {resumen[grado]}"
    for s in estudiantes:                                             # áreas listadas = columna Áreas (bajo)
        assert len(s["a"]) == s["nb"], f"Áreas no cuadran para {s['n']}"
    print(f"✔ Verificado: {len(estudiantes)} estudiantes, {sum(s['nb'] for s in estudiantes)} áreas en bajo")


def leer_promo_comite(estudiantes):
    """Devuelve los nombres de PROMO_COMITE y verifica que existan en el grado indicado."""
    nombres = []
    for grado, nombre in PROMO_COMITE:
        assert any(s["g"] == grado and s["n"] == nombre for s in estudiantes), \
            f"No se encontró a {nombre} en {grado}"
        nombres.append(nombre)
    return nombres


def anonimizar(estudiantes, casos, promo):
    """Reemplaza nombres por un código (E-001...) e iniciales. Mantiene intacto todo lo demás."""
    mapa = {}                                          # nombre real -> código
    for k, s in enumerate(estudiantes, start=1):
        iniciales = ".".join(p[0] for p in s["n"].split()) + "."   # "PEREZ GOMEZ ANA" -> "P.G.A."
        mapa[s["n"]] = f"E-{k:03d} ({iniciales})"      # ej. "E-007 (P.G.A.)"
    for s in estudiantes:
        s["n"] = mapa[s["n"]]                          # cambia el nombre en el estudiante
        s.pop("raw", None)                             # quita el texto original (no contiene nombres, pero no se usa)
    casos = [mapa.get(c, c) for c in casos]            # aplica el mismo código en la lista de casos
    promo = [mapa.get(c, c) for c in promo]            # y en la lista de promovidos por el comité
    return estudiantes, casos, promo


def main():
    parser = argparse.ArgumentParser(description="Genera el dashboard de reprobación")
    parser.add_argument("--excel", default=str(RAIZ / "data" / "Listado_reprobados_secundaria_2026.xlsx"),
                        help="Ruta del Excel de origen")
    parser.add_argument("--anonimo", action="store_true", help="Genera versión sin nombres")
    args = parser.parse_args()

    libro = openpyxl.load_workbook(args.excel, data_only=True)  # data_only=True lee valores, no fórmulas
    estudiantes = leer_estudiantes(libro)
    casos = leer_casos(libro)
    verificar(estudiantes, libro)
    promo = leer_promo_comite(estudiantes)

    if args.anonimo:
        estudiantes, casos, promo = anonimizar(estudiantes, casos, promo)
        salida = RAIZ / "index_anonimo.html"
    else:
        salida = RAIZ / "index.html"

    datos = {"studs": estudiantes, "casos": casos, "promo": promo}
    (RAIZ / "data" / ("data_anonimo.json" if args.anonimo else "data.json")).write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")   # copia legible de los datos

    plantilla = (RAIZ / "src" / "template.html").read_text(encoding="utf-8")   # lee la plantilla
    html = plantilla.replace("__DATA__", json.dumps(datos, ensure_ascii=False))  # inserta los datos
    escudo = (RAIZ / "assets" / "escudo.webp").read_bytes()                  # lee la imagen del escudo
    logo = "data:image/webp;base64," + base64.b64encode(escudo).decode()     # la convierte en texto (data URI)
    html = html.replace("__LOGO__", logo)                                     # la inserta en el encabezado y el pie
    if args.anonimo:   # en la versión anónima se ajusta la leyenda del pie de página
        html = html.replace("Contiene datos personales de estudiantes — uso institucional reservado.",
                            "Versión anonimizada: nombres reemplazados por códigos.")
    salida.write_text(html, encoding="utf-8")          # escribe el HTML final
    print(f"✔ Generado: {salida.name}")


if __name__ == "__main__":   # solo se ejecuta si se llama directamente (no si se importa)
    main()
