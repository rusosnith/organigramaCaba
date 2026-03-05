import pandas as pd
import unicodedata
import re
from pathlib import Path

# Normalize name for consistent comparison
def normalize(name: str) -> str:
    if pd.isna(name):
        return ''
    # lowercase, strip accents, keep letters and space
    n = name.lower()
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    n = re.sub(r'[^a-z\s]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

# Load names file
nombres_path = Path(__file__).parent / 'nombres.csv'
df_nombres = pd.read_csv(nombres_path, dtype=str)

# Build mapping from normalized name -> set of genders
name_genders = {}
for _, row in df_nombres.iterrows():
    nombre = normalize(row['nombre'])
    sexo = row['sexo'].strip().upper() if pd.notna(row['sexo']) else ''
    if not nombre or sexo not in ('M', 'F'):
        continue
    if nombre not in name_genders:
        name_genders[nombre] = set()
    name_genders[nombre].add(sexo)

# Load funcionarios file
func_path = Path(__file__).parent / 'funcionarios_unificados_limpioOK.csv'
df = pd.read_csv(func_path, dtype=str)

# Ensure genero column exists
if 'genero' not in df.columns:
    df['genero'] = ''

# Track changes
assigned = 0
ambiguous = 0

for idx, row in df.iterrows():
    gen = row.get('genero', '')
    if pd.isna(gen) or gen == '':
        nombre_completo = row.get('nombre', '')
        norm = normalize(nombre_completo).split(' ')[0]  # first token
        if norm in name_genders:
            genders = name_genders[norm]
            if len(genders) == 1:
                new_gen = next(iter(genders))
                df.at[idx, 'genero'] = new_gen
                assigned += 1
            else:
                # ambiguous, leave blank
                ambiguous += 1
        else:
            # no data
            pass

print(f"Total filas procesadas: {len(df)}")
print(f"Géneros asignados: {assigned}")
print(f"Ambiguos sin asignar: {ambiguous}")

# Save updated file
out_path = Path(__file__).parent / 'funcionarios_unificados_limpioOK.csv'
df.to_csv(out_path, index=False)
print(f"Archivo actualizado guardado en {out_path}")
