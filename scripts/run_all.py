import pandas as pd
import re
import unicodedata
from pathlib import Path

# utilities

def detect_separator(path, encoding):
    try:
        with open(path, 'r', encoding=encoding) as f:
            line = f.readline()
        return ';' if line.count(';') > line.count(',') else ','
    except:
        return ','

def normalize_name(name: str) -> str:
    if pd.isna(name):
        return ''
    n = name.lower()
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    n = re.sub(r'[^a-z\s]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

# 1. unify CSVs
print('=== Unifying year CSVs ===')
root = Path(__file__).parent.parent  # project root
data_raw = root / 'data' / 'raw'
files = sorted(data_raw.glob('autoridades*.csv'))
dfs = []
for f in files:
    print(' processing', f.name)
    year_match = re.search(r'(\d{4})', f.name)
    if not year_match:
        continue
    year = int(year_match.group(1))
    df = None
    for enc in ['utf-8','latin-1','iso-8859-1','cp1252']:
        sep = detect_separator(f, enc)
        try:
            df = pd.read_csv(f, encoding=enc, sep=sep, low_memory=False, on_bad_lines='skip')
            print('   read with', enc, 'sep', sep)
            break
        except Exception:
            continue
    if df is not None:
        df['año'] = year
        dfs.append(df)
    else:
        print('  failed to read', f.name)

if not dfs:
    raise RuntimeError('no input data')
df_all = pd.concat(dfs, ignore_index=True)

# 2. normalise columns (no automatic dedupe to avoid merging columns with data in both)
print('=== Normalising columns ===')
def normal_col(col):
    return normalize_name(col).replace(' ', '_')

seen = set()
rename = {}
for col in df_all.columns:
    n = normal_col(col)
    if n in seen:
        i = 1
        while f"{n}_{i}" in seen:
            i += 1
        n = f"{n}_{i}"
    seen.add(n)
    rename[col] = n
df_all.rename(columns=rename, inplace=True)

# manual merges for known duplicates
if 'reparticion' in df_all.columns and 'descripcion_reparticion' in df_all.columns:
    df_all['reparticion'] = df_all['reparticion'].fillna(df_all['descripcion_reparticion'])
    df_all.drop(columns=['descripcion_reparticion'], inplace=True)

# 3 infer gender by CUIT
print('=== Inferring gender from cuil ===')
def infer_from_cuit(c):
    try:
        s = str(c).replace('-', '').strip()
        if len(s) >= 2:
            p = s[:2]
            if p == '20': return 'M'
            if p == '27': return 'F'
    except: pass
    return None

if 'genero' not in df_all.columns:
    df_all['genero'] = pd.NA
mask = df_all['genero'].isna()
inf = df_all.loc[mask, 'cuil'].apply(infer_from_cuit)
df_all.loc[mask, 'genero'] = df_all.loc[mask, 'genero'].fillna(inf)

# 4 parse name-gender table
print('=== Parsing name list ===')
names_html = data_raw / 'nombres.html'
name_gender = {}
if names_html.exists():
    import html
    text = names_html.read_text(encoding='iso-8859-1', errors='ignore')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, flags=re.DOTALL|re.IGNORECASE)
    for tr in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.DOTALL|re.IGNORECASE)
        if len(tds) >= 2:
            n = re.sub(r'<[^>]+>', '', tds[0]).strip()
            s = re.sub(r'<[^>]+>', '', tds[1]).strip().upper()
            if n and s in ('M','F'):
                norm = normalize_name(n).split(' ')[0]
                name_gender.setdefault(norm, set()).add(s)
else:
    print('no names.html file, skipping')

# 5 assign missing genders from name list
print('=== Assigning gender from name list ===')
assigned = 0
for idx, row in df_all[df_all['genero'].isna()].iterrows():
    first = normalize_name(str(row.get('nombre',''))).split(' ')[0]
    if first in name_gender and len(name_gender[first]) == 1:
        df_all.at[idx,'genero'] = next(iter(name_gender[first]))
        assigned += 1
print('assigned from names', assigned)

# manual merges for known duplicates (only if one is empty)
print('=== Merging known duplicate columns ===')
if 'ministerionombre' in df_all.columns and 'ministerio' in df_all.columns:
    df_all['ministerio'] = df_all['ministerio'].fillna(df_all['ministerionombre'])
    df_all.drop(columns=['ministerionombre'], inplace=True)
if 'descrep' in df_all.columns and 'ministerio' in df_all.columns:
    df_all['ministerio'] = df_all['ministerio'].fillna(df_all['descrep'])
    df_all.drop(columns=['descrep'], inplace=True)
if 'descsigla' in df_all.columns and 'ministerio' in df_all.columns:
    df_all['ministerio'] = df_all['ministerio'].fillna(df_all['descsigla'])
    df_all.drop(columns=['descsigla'], inplace=True)

processed_dir = root / 'data' / 'processed'
# final save
out_final = processed_dir / 'funcionarios_unificados_limpioOK.csv'
df_all.to_csv(out_final, index=False)
print('final file created', out_final)
