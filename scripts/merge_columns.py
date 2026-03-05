import pandas as pd

df = pd.read_csv('funcionarios_unificados_limpioOK.csv')

# Combinar reparticion y descripcion_reparticion
df['reparticion'] = df['reparticion'].fillna(df['descripcion_reparticion'])

# Eliminar la columna descripcion_reparticion
df.drop(columns=['descripcion_reparticion'], inplace=True)

# Guardar
df.to_csv('funcionarios_unificados_limpioOK.csv', index=False)

print('✓ Columnas unificadas')
print(f'  reparticion: {df["reparticion"].notna().sum()} valores')
print(f'  descripcion_reparticion eliminada')
print(f'\nColumnas finales ({len(df.columns)}):')
print('-' * 40)
for col in df.columns:
    print(f'  • {col}')
