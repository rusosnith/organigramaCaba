import re
from pathlib import Path

input_path = Path(__file__).parent / 'nombres'
output_path = Path(__file__).parent / 'nombres_limpios.csv'

valid_lines = []
removed_count = 0

with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if i < 10:
            print('LINE', i, repr(line))
        line = line.rstrip('\n')
        if not line:
            continue
        # Expect format Nombre,Sexo,
        parts = line.split(',')
        if len(parts) < 2:
            removed_count += 1
            continue
        name = parts[0].strip()
        sex = parts[1].strip().upper()
        # filter by sex letter M or F
        if sex not in ('M', 'F'):
            removed_count += 1
            continue
        # length too long
        if len(name) > 30:
            removed_count += 1
            continue
        # check uppercase (ignoring accents and hyphens/spaces)
        clean_name = re.sub(r'[^A-Za-z]', '', name)
        if clean_name and clean_name.upper() == clean_name:
            removed_count += 1
            continue
        # filter out weird lines not matching allowed pattern
        valid_lines.append(f"{name},{sex}")

with open(output_path, 'w', encoding='utf-8') as f:
    for l in valid_lines:
        f.write(l + '\n')

print(f"Registros originales: se procesó {len(valid_lines) + removed_count}")
print(f"Registros válidos guardados: {len(valid_lines)}")
print(f"Registros eliminados: {removed_count}")
