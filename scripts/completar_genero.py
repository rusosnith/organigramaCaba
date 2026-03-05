import pandas as pd
import numpy as np

df = pd.read_csv('funcionarios_unificados_limpioOK.csv')

print('Antes de completar géneros:')
print(f'  Total de registros: {len(df)}')
print(f'  Con género: {df["genero"].notna().sum()}')
print(f'  Sin género: {df["genero"].isna().sum()}')

# Función para extraer género del CUIT
def inferir_genero_desde_cuit(cuit):
    """
    Infiere el género desde el CUIT
    - 20: Masculino (DNI hombre)
    - 27: Femenino (DNI mujer)
    """
    if pd.isna(cuit):
        return np.nan
    
    # Convertir a string y eliminar caracteres especiales
    cuit_str = str(cuit).replace('-', '').replace(' ', '').strip()
    
    # Extraer los primeros 2 dígitos
    if len(cuit_str) >= 2:
        prefijo = cuit_str[:2]
        if prefijo == '20':
            return 'M'
        elif prefijo == '27':
            return 'F'
    
    return np.nan

# Completar género usando CUIT
print('\nCompletando géneros usando CUIT...')

# Crear una copia de la columna género
genero_nuevo = df['genero'].copy()

# Para registros sin género pero con CUIT
mask_sin_genero = genero_nuevo.isna()
print(f'  Registros sin género: {mask_sin_genero.sum()}')

# Intentar inferir género desde CUIT
genero_inferred = df.loc[mask_sin_genero, 'cuil'].apply(inferir_genero_desde_cuit)

# Contar cuántos se pueden inferir
completados = genero_inferred.notna().sum()
print(f'  Géneros completados desde CUIT: {completados}')

# Actualizar la columna
genero_nuevo[mask_sin_genero] = genero_inferred

df['genero'] = genero_nuevo

print('\nDespués de completar géneros:')
print(f'  Total de registros: {len(df)}')
print(f'  Con género: {df["genero"].notna().sum()}')
print(f'  Sin género: {df["genero"].isna().sum()}')

# Mostrar distribución
print('\nDistribución de géneros:')
print(f'  M (Masculino): {(df["genero"] == "M").sum()}')
print(f'  F (Femenino): {(df["genero"] == "F").sum()}')
print(f'  Sin identificar: {df["genero"].isna().sum()}')

# Guardar
df.to_csv('funcionarios_unificados_limpioOK.csv', index=False)
print('\n✓ Archivo actualizado: funcionarios_unificados_limpioOK.csv')
