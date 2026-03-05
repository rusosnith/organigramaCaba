import pandas as pd
import re
from pathlib import Path
from unicodedata import normalize

# Función para normalizar nombres de columnas
def normalizar_nombre(nombre):
    """Normaliza un nombre: minúsculas, sin acentos, sin caracteres especiales"""
    nombre = nombre.lower()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if not diacritic_check(c))
    nombre = re.sub(r'[^a-z0-9_]', '', nombre)
    return nombre

def diacritic_check(c):
    """Verifica si un carácter es un diacrítico"""
    import unicodedata
    return unicodedata.category(c) == 'Mn'

# Leer el archivo unificado
archivo_unificado = Path(__file__).parent / 'funcionarios_unificados.csv'

print("Leyendo archivo unificado...")
df = pd.read_csv(archivo_unificado, low_memory=False)

print(f"Columnas originales: {len(df.columns)}")

# Crear un mapeo de columnas normalizadas
mapeo_normalizacion = {}
columnas_normalizadas = {}

for col in df.columns:
    col_normalizada = normalizar_nombre(col)
    mapeo_normalizacion[col] = col_normalizada
    
    if col_normalizada not in columnas_normalizadas:
        columnas_normalizadas[col_normalizada] = []
    columnas_normalizadas[col_normalizada].append(col)

# Encontrar columnas duplicadas
columnas_duplicadas = {k: v for k, v in columnas_normalizadas.items() if len(v) > 1}

print(f"Se encontraron {len(columnas_duplicadas)} grupos de columnas duplicadas")
print("\nUnificando columnas...")
print("-" * 80)

# Unifcar columnas duplicadas
columnas_para_eliminar = []

for col_normalizada, cols_originales in sorted(columnas_duplicadas.items()):
    # Ordenar para que tengamos un orden consistente
    cols_ordenadas = sorted(cols_originales)
    
    print(f"\nUnificando: {col_normalizada}")
    print(f"  Columnas: {cols_ordenadas}")
    
    # Crear nueva columna combinando todas las variantes
    # Usar la primera columna y llenar los nulos con valores de las otras
    nueva_columna = df[cols_ordenadas[0]].copy()
    
    for col in cols_ordenadas[1:]:
        # Llenar valores nulos en nueva_columna con valores de col
        mask = nueva_columna.isna()
        nueva_columna[mask] = df.loc[mask, col]
    
    # Reemplazar la primera columna con la versión combinada
    df[cols_ordenadas[0]] = nueva_columna
    
    # Renombrar la primera columna al nombre normalizado
    if cols_ordenadas[0] != col_normalizada:
        df.rename(columns={cols_ordenadas[0]: col_normalizada}, inplace=True)
        columnas_para_eliminar.extend(cols_ordenadas[1:])
    else:
        columnas_para_eliminar.extend(cols_ordenadas[1:])
    
    valores_no_nulos = nueva_columna.notna().sum()
    print(f"  ✓ Nuevos valores no nulos: {valores_no_nulos}")

# Eliminar columnas duplicadas
print("\n" + "=" * 80)
print("Eliminando columnas duplicadas...")
print(f"Columnas a eliminar ({len(columnas_para_eliminar)}):")
for col in sorted(set(columnas_para_eliminar)):
    print(f"  - {col}")

df.drop(columns=columnas_para_eliminar, inplace=True)

# Normalizar TODAS las columnas restantes a minúsculas con guion bajo
print("\n" + "=" * 80)
print("Normalizando nombres de todas las columnas...")

# Agrupar por nombre normalizado para eliminar cualquier variante restante
mapeo_final = {}
for col in df.columns:
    col_norm = normalizar_nombre(col)
    if col_norm not in mapeo_final:
        mapeo_final[col_norm] = col

# Renombrar todas las columnas
rename_dict = {col: normalizar_nombre(col) for col in df.columns}
df.rename(columns=rename_dict, inplace=True)

# Eliminar duplicados finales por si quedan
df = df.loc[:, ~df.columns.duplicated()]

print(f"Columnas finales: {len(df.columns)}")
print("\nNuevas columnas:")
print("-" * 80)
for col in sorted(df.columns):
    print(f"  • {col}")

# Guardar el archivo limpio
archivo_salida = Path(__file__).parent / 'funcionarios_unificados_limpio.csv'
df.to_csv(archivo_salida, index=False)

print("\n" + "=" * 80)
print(f"✓ Archivo limpio guardado: funcionarios_unificados_limpio.csv")
print(f"  Registros: {len(df):,}")
print(f"  Columnas: {len(df.columns)}")
print(f"  Reducción: {46 - len(df.columns)} columnas eliminadas")
