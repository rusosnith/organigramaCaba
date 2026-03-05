import pandas as pd
import re
from pathlib import Path
from unicodedata import normalize

# Función para normalizar nombres de columnas
def normalizar_nombre(nombre):
    """
    Normaliza un nombre: minúsculas, sin acentos, sin caracteres especiales
    Solo mantiene letras, números y guiones bajos
    """
    # Convertir a minúsculas
    nombre = nombre.lower()
    
    # Remover acentos
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if not diacritic_check(c))
    
    # Remover caracteres especiales (mantener solo letras, números y _)
    nombre = re.sub(r'[^a-z0-9_]', '', nombre)
    
    return nombre

def diacritic_check(c):
    """Verifica si un carácter es un diacrítico"""
    import unicodedata
    return unicodedata.category(c) == 'Mn'

# Leer el archivo unificado
archivo_unificado = Path(__file__).parent / 'funcionarios_unificados.csv'

print("Leyendo archivo unificado...")
df = pd.read_csv(archivo_unificado)

print(f"\nColumnas originales ({len(df.columns)}):")
print("-" * 80)
for col in sorted(df.columns):
    print(f"  {col}")

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
print("\n" + "=" * 80)
print("ANÁLISIS DE COLUMNAS DUPLICADAS")
print("=" * 80)

columnas_duplicadas = {k: v for k, v in columnas_normalizadas.items() if len(v) > 1}

if columnas_duplicadas:
    print(f"\nSe encontraron {len(columnas_duplicadas)} grupos de columnas que podrían unificarse:\n")
    
    for col_normalizada, cols_originales in sorted(columnas_duplicadas.items()):
        print(f"Nombre normalizado: '{col_normalizada}'")
        print(f"  Columnas encontradas ({len(cols_originales)}):")
        for col in cols_originales:
            valores_no_nulos = df[col].notna().sum()
            print(f"    - '{col}' ({valores_no_nulos} valores no nulos)")
        print()
else:
    print("\n✓ No se encontraron columnas duplicadas o similares")

# Mostrar resumen de unificación
print("=" * 80)
print("SUGERENCIA DE UNIFICACIÓN")
print("=" * 80)

if columnas_duplicadas:
    print("\nPara unificar, podría:")
    print("- Crear una nueva columna con el nombre normalizado")
    print("- Combinar los valores de todas las variantes")
    print("- Eliminar las columnas originales")
    print("\nLas columnas a unificar son:")
    for col_normalizada, cols_originales in sorted(columnas_duplicadas.items()):
        print(f"\n  '{col_normalizada}':")
        for col in cols_originales:
            print(f"    ← '{col}'")
