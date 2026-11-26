# Dashboard de reprobación · Secundaria 2026

**I.E. San Pedro y San Pablo — Comité de Evaluación y Promoción**

Dashboard interactivo con los estudiantes reprobados del período final 2026 (grados 6-1 a 11-1). Se construyó solo con los datos del archivo del Comité y no modifica ninguno.

> ⚠️ **Uso institucional reservado.** `index.html` y `data/` contienen nombres de estudiantes menores de edad. Este repositorio debe ser **privado**. Para compartir fuera del comité usa `index_anonimo.html`.

## Contenido

| Archivo | Qué es |
|---|---|
| `index.html` | Dashboard completo, con nombres. Se abre con doble clic y funciona sin internet. |
| `index_anonimo.html` | Misma versión, con los nombres cambiados por códigos (E-001 + iniciales). |
| `data/Listado_reprobados_secundaria_2026.xlsx` | Archivo original del Comité (fuente). |
| `data/data.json`, `data/data_anonimo.json` | Datos extraídos del Excel, en formato legible. |
| `src/template.html` | Plantilla del dashboard: diseño, gráficos y filtros (colores institucionales). |
| `assets/escudo.webp` | Escudo del colegio; el script lo incrusta dentro del HTML. |
| `scripts/build.py` | Script que lee el Excel, verifica los totales y genera los HTML. |

## Qué muestra

- **Filtros:** grado (permite marcar varios), desempeño, número de áreas perdidas y búsqueda por nombre.
- **Indicadores:** reprobados, áreas en bajo, promedio final, inasistencias, estudiantes que pierden 1 área y estudiantes que pierden 4 o más.
- **Hallazgos clave:** se recalculan con cada filtro.
- **Gráficos:** reprobados por grado; distribución de áreas perdidas; áreas con más reprobación; mapa de calor grado × área; inasistencias frente a promedio final; severidad de las valoraciones por área.
- **Casos prioritarios de revisión:** estudiantes con 1 sola área perdida, valoración ≥ 2,7 y promedio final ≥ 3,7 (18 casos: los 11 de la hoja «Casos 1 área» y 7 nuevos). Incluye un gráfico por grado (8-1 y 10-1 son los que más tienen) y un filtro «Revisión → Prioritarios».
- **Tabla de detalle por estudiante:** se puede ordenar y marca quién es «Prioritario» y quién es «Caso comité».
- Tema claro/oscuro y versión para imprimir.

## Regenerar el dashboard (si cambian los datos)

```bash
pip install -r requirements.txt               # instala openpyxl (una sola vez)
python scripts/build.py                       # genera index.html
python scripts/build.py --anonimo             # genera index_anonimo.html
```

Para usar otro Excel con la misma estructura:

```bash
python scripts/build.py --excel ruta/al/archivo.xlsx
```

El script comprueba que los totales coincidan con la hoja «Resumen» (100 estudiantes, 353 áreas en bajo). Si algo no cuadra, se detiene y no genera el dashboard.

## Notas metodológicas

- Inasistencias = columna TOTAL del archivo original.
- DISCP se registra aparte y no cuenta como área perdida.
- En 10-1 aparece «Área sin rótulo (col. M)»; se conserva tal como viene en el archivo.
- El criterio de casos prioritarios está definido en `src/template.html` (constante `PRIO`). La hoja «Casos 1 área» usa límites estrictos (> 2,7 y > 3,7). La decisión final la toma el comité según el SIEE.
- Los tramos (1 / 2–3 / 4 o más áreas) y los colores por valoración son agrupaciones de lectura. No son criterios de promoción.
