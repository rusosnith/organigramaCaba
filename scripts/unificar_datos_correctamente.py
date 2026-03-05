import pandas as pd
from pathlib import Path

# Mapeo semántico de columnas
# Agrupa todas las variantes de una columna bajo un nombre estándar
MAPEO_SEMANTICO = {
    'ministerio': ['ministerio_nombre', 'MINISTERIO', 'ministerio'],
    'reparticion': ['reparticion_nombre', 'DESC_REP', 'dependencia_nombre', 'desc_rep'],
    'sigla': ['sigla', 'SIGLA'],
    'codigo_reparticion': ['codigo_reparticion', 'COD_REP', 'cod_rep'],
    'apellido': ['apellido', 'AYN', 'ayn'],
    'nombre': ['nombre'],
    'descripcion_sigla': ['descripcion_sigla', 'DESC_SIGLA', 'desc_sigla'],
    'descripcion_reparticion': ['descripcion_reparticion'],
    'genero': ['genero', 'SEXO', 'sexo'],
    'email': ['email', 'MAIL_LABORAL', 'mail_laboral'],
    'cuil': ['cuil', 'CUIL'],
    'escalafon': ['escalafon', 'ESCALAFON'],
    'puesto': ['puesto', 'LIT_PUESTO', 'lit_puesto'],
    'rol_desde': ['rol_desde', 'ROL_DESDE'],
    'rol_hasta': ['rol_hasta', 'ROL_HASTA'],
    'edad': ['edad', 'EDAD'],
    'car_sit_rev': ['CAR_SIT_REV', 'car_sit_rev'],
    'reporta_a': ['reporta_a', 'reporta a '],
    'nivel': ['nivel'],
    'nivel_2': ['nivel_2']
}

# Leer el archivo unificado original
archivo_unificado = Path(__file__).parent / 'funcionarios_unificados.csv'
print("Leyendo archivo unificado original...")
df = pd.read_csv(archivo_unificado, low_memory=False)

print(f"Registros originales: {len(df)}")
print(f"Columnas originales: {len(df.columns)}")

# Crear nuevo dataframe con columnas normalizadas
df_nuevo = pd.DataFrame()
df_nuevo['año'] = df['año']

# Aplicar mapeo semántico
print("\nMapeando columnas...")
print("-" * 80)

for col_estandar, variantes in MAPEO_SEMANTICO.items():
    # Encontrar qué variantes existen en el dataframe
    columnas_disponibles = [v for v in variantes if v in df.columns]
    
    if columnas_disponibles:
        print(f"\n{col_estandar}:")
        
        # Crear columna nueva combinando todas las variantes
        nueva_columna = pd.Series(index=df.index, dtype='object', data=None)
        
        for col_var in columnas_disponibles:
            # Llenar valores nulos con valores de esta variante
            mask = nueva_columna.isna()
            nueva_columna[mask] = df.loc[mask, col_var]
            
            valores = df[col_var].notna().sum()
            print(f"  ← {col_var}: {valores} valores")
        
        valores_finales = nueva_columna.notna().sum()
        print(f"  → Total: {valores_finales} valores")
        
        df_nuevo[col_estandar] = nueva_columna

# Reorganizar columnas para mejor legibilidad
columnas_orden = [
    'año', 'ministerio', 'reparticion', 'sigla', 'codigo_reparticion',
    'apellido', 'nombre', 'email', 'cuil', 'genero', 'edad',
    'escalafon', 'puesto', 'rol_desde', 'rol_hasta',
    'descripcion_sigla', 'descripcion_reparticion', 'reporta_a',
    'nivel', 'nivel_2', 'car_sit_rev'
]

# Mantener solo las columnas que existen
columnas_finales = [c for c in columnas_orden if c in df_nuevo.columns]
df_nuevo = df_nuevo[columnas_finales]

# Guardar el archivo
archivo_salida = Path(__file__).parent / 'funcionarios_unificados_limpioOK.csv'
df_nuevo.to_csv(archivo_salida, index=False)

print("\n" + "=" * 80)
print(f"✓ Archivo guardado: funcionarios_unificados_limpioOK.csv")
print(f"  Registros: {len(df_nuevo):,}")
print(f"  Columnas: {len(df_nuevo.columns)}")
print(f"\nColumnas finales:")
for i, col in enumerate(df_nuevo.columns, 1):
    print(f"  {i}. {col}")

# Mostrar resumen por año
print("\n" + "=" * 80)
print("Resumen de datos por año:")
print("-" * 80)

for año in sorted(df_nuevo['año'].unique()):
    df_año = df_nuevo[df_nuevo['año'] == año]
    campos_con_datos = 0
    for col in df_año.columns:
        if col != 'año' and df_año[col].notna().sum() > 0:
            campos_con_datos += 1
    
    print(f"{int(año)}: {len(df_año):>5} registros | {campos_con_datos:>2} campos con datos")
