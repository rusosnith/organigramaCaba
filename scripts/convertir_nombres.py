import pandas as pd
from pathlib import Path

input_path = Path(__file__).parent / 'nombres.html'
output_path = Path(__file__).parent / 'nombres.csv'

import re

# We'll extract rows from table manually using regex
with open(input_path, 'r', encoding='iso-8859-1', errors='ignore') as f:
    html_text = f.read()

# find all <tr ...> ... </tr> blocks (with potential attributes)
trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html_text, flags=re.DOTALL|re.IGNORECASE)
print(f"Encontradas {len(trs)} filas TR")
# debug sample of first few rows
rows = []
for idx, tr in enumerate(trs[:5]):
    print('TR sample', idx, repr(tr[:200]))

# now process all rows
for tr in trs:
    tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.DOTALL|re.IGNORECASE)
    if len(tds) >= 2:
        def clean(cell):
            cell = re.sub(r'<[^>]+>', '', cell)
            return cell.strip()
        nombre = clean(tds[0])
        sexo = clean(tds[1])
        if nombre and sexo:
            rows.append((nombre, sexo))

# write CSV
with open(output_path, 'w', encoding='utf-8') as out:
    out.write('nombre,sexo\n')
    for nombre, sexo in rows:
        out.write(f'{nombre},{sexo}\n')

print(f'Se extrajeron {len(rows)} filas y guardaron en {output_path}')
