# Organigrama CABA Data Pipeline

Este repositorio contiene un conjunto de scripts y datos para unificar y limpiar el
histórico de funcionarios de la Ciudad Autónoma de Buenos Aires (CABA).

## Estructura de carpetas

```
organigramaCaba/
├─ data/
│  ├─ raw/              # Archivos originales descargados
│  │  ├─ autoridades*.csv  # CSV por año
│  │  ├─ nombres.html      # tabla de nombres con sexo
│  │  └─ nombres.csv       # exportación simplificada (nombre,sexo)
│  └─ processed/        # Resultados intermedios y finales
│     ├─ funcionarios_unificados.csv
│     ├─ funcionarios_intermedio.csv
│     ├─ funcionarios_unificados_limpioOK.csv
│     └─ nombres_limpios.csv  (# opciona)
├─ scripts/             # Script principal para ejecutar el pipeline completo
│  └─ run_all.py        # pipeline completo
└─ README.md
```

## Uso

1. Colocar los CSV de cada año en `data/raw/` (ya están allí). También agregar
   el `nombres.html` con la tabla de nombres.
2. Ejecutar el pipeline completo:
   ```bash
   python scripts/run_all.py
   ```
   Esto genera el archivo final `data/processed/funcionarios_unificados_limpioOK.csv`.
3. Si necesitas rehacer un paso individual, modifica el script `run_all.py`.

## Notas

- El pipeline detecta automáticamente codificaciones y separadores de los CSV.
- Se normalizan y unifican columnas con variantes y se infiere género por CUIT y
  por comparación con la lista de nombres.
- El repositorio está preparado para versionarse: solo hace falta inicializar un
  repositorio Git aquí y hacer commit.

## Inconsistencias y Problemas en los Datos

Los datasets originales presentaban múltiples inconsistencias y problemas que hicieron necesario el desarrollo de este pipeline complejo. A continuación, se detallan todas las issues identificadas:

- **Codificaciones inconsistentes**: Los archivos CSV usaban diferentes codificaciones (UTF-8, Latin-1, ISO-8859-1, CP1252), lo que causaba errores al leer caracteres especiales como acentos y ñ.
- **Separadores mixtos**: Algunos archivos estaban separados por comas (`,`), otros por punto y coma (`;`), requiriendo detección automática para evitar errores de parsing.
- **Columnas duplicadas con variaciones**: Múltiples columnas representaban la misma información pero con nombres ligeramente diferentes (ej: "reparticion" vs "Repartición", con acentos, mayúsculas/minúsculas, caracteres especiales), necesitando normalización y unificación.
- **Datos faltantes en años posteriores**: Desde 2021 en adelante, muchas filas estaban completamente vacías o con datos incompletos, requiriendo mapeo semántico para rellenar campos basados en nombres similares de años anteriores.
- **Género no presente inicialmente**: La columna de género faltaba en los datos originales, obligando a inferirlo mediante reglas (CUIT empezando con 20 = masculino, 27 = femenino) y comparación con una lista externa de nombres.
- **Lista de nombres en formato HTML**: La fuente de géneros por nombre venía en una tabla HTML con entradas inválidas (filas que no eran nombres, textos demasiado largos, entradas en mayúsculas completas), requiriendo parsing y filtrado.
- **Géneros ambiguos**: Algunos nombres en la lista tenían géneros asignados de manera inconsistente o ambigua, por lo que se optó por no asignar género en casos dudosos para evitar errores.
- **Falta de estandarización en nombres y textos**: Nombres de funcionarios, reparticiones y descripciones contenían inconsistencias en formato, acentos y caracteres especiales, necesitando limpieza y normalización.
- **Columnas redundantes fusionadas**: Campos como `ministerionombre`, `descrep` y `descsigla` que duplicaban información del ministerio fueron unificados en una sola columna `ministerio`.

Estos problemas hicieron indispensable el desarrollo de un pipeline robusto con detección automática, normalización, inferencia de datos y limpieza exhaustiva para obtener un dataset unificado y usable.

## Contribuciones

Puedes agregar mejoras organizando, corrigiendo o extendiendo los scripts. La
estructura actual facilita reproducir el proceso completo desde cero.
