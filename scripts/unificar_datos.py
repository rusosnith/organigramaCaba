import pandas as pd
import os
import re
from pathlib import Path

# Función para detectar el separador del CSV
def detectar_separador(archivo, encoding):
    """Detecta si el archivo usa coma o punto y coma como separador"""
    try:
        with open(archivo, 'r', encoding=encoding) as f:
            primera_linea = f.readline()
        # Si hay más puntos y comas que comas, probablemente usa ;
        if primera_linea.count(';') > primera_linea.count(','):
            return ';'
        else:
            return ','
    except:
        return ','

# Obtener la ruta del directorio actual
directorio = Path(__file__).parent

# Buscar todos los archivos CSV
archivos_csv = list(directorio.glob('autoridades*.csv'))

# Ordenar archivos por año
archivos_csv.sort()

print(f"Se encontraron {len(archivos_csv)} archivos CSV")

# Lista para almacenar los dataframes
dataframes = []

# Procesar cada archivo
for archivo in archivos_csv:
    print(f"Procesando: {archivo.name}")
    
    # Extraer el año del nombre del archivo
    match = re.search(r'(\d{4})', archivo.name)
    if match:
        año = match.group(1)
        
        # Intentar leer el CSV con diferentes encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                # Detectar el separador para este archivo y encoding
                sep = detectar_separador(archivo, encoding)
                
                df = pd.read_csv(archivo, encoding=encoding, sep=sep, low_memory=False, on_bad_lines='skip')
                print(f"  ✓ Leído con encoding: {encoding}, separador: '{sep}'")
                break
            except Exception as e:
                continue
        
        if df is not None:
            # Agregar la columna de año
            df['año'] = int(año)
            
            # Agregar a la lista
            dataframes.append(df)
        else:
            print(f"  ERROR: No se pudo leer {archivo.name} con ningún encoding")
    else:
        print(f"  ADVERTENCIA: No se pudo extraer el año de {archivo.name}")

# Unificar todos los dataframes
if dataframes:
    df_unificado = pd.concat(dataframes, ignore_index=True)
    
    # Reordenar las columnas para que 'año' esté al final
    columnas = list(df_unificado.columns)
    if 'año' in columnas:
        columnas.remove('año')
        columnas.append('año')
        df_unificado = df_unificado[columnas]
    
    # Guardar el archivo unificado
    archivo_salida = directorio / 'funcionarios_unificados.csv'
    df_unificado.to_csv(archivo_salida, index=False)
    
    print(f"\n✓ Archivo unificado creado: {archivo_salida.name}")
    print(f"  Total de registros: {len(df_unificado):,}")
    print(f"  Años incluidos: {sorted(df_unificado['año'].unique())}")
    print(f"  Columnas: {', '.join(df_unificado.columns.tolist())}")
else:
    print("No se encontraron archivos CSV para procesar")
