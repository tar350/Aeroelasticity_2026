import re
import csv
from pathlib import Path

project_root = Path(r"C:\CFD+FEA project\Aeroelasticity")
input_dir = project_root / "outputs" / "avl_validation"
output_dir = input_dir / "manual_exports"
output_dir.mkdir(parents=True, exist_ok=True)

rho = 1.225
V = 40.0
q = 0.5 * rho * V**2

# Find alpha 4 strip-force file
candidates = list(input_dir.glob("*p4*strip_forces.txt")) + list(input_dir.glob("*alpha4*strip_forces.txt"))

if not candidates:
    raise FileNotFoundError("Could not find alpha 4 strip-force file. Check outputs/avl_validation folder.")

fs_file = candidates[0]
print(f"Using strip-force file: {fs_file}")

lines = fs_file.read_text(errors="ignore").splitlines()

rows = []

for line in lines:
    stripped = line.strip()

    # AVL strip data rows usually begin with an integer strip index.
    if not re.match(r"^\d+\s+", stripped):
        continue

    nums = re.findall(r"[-+]?\d*\.\d+(?:[Ee][-+]?\d+)?|[-+]?\d+(?:[Ee][-+]?\d+)?", stripped)

    if len(nums) < 8:
        continue

    vals = [float(x) for x in nums]

    # Common AVL FS format:
    # j, Xle, Yle, Zle, Chord, Area, c_cl, ai, ...
    # Some formats include cl instead of c_cl, but AVL often provides c cl.
    j = int(vals[0])
    xle = vals[1]
    y = vals[2]
    zle = vals[3]
    chord = vals[4]
    area = vals[5]

    # Best interpretation for AVL strip-force output:
    # column after Area is often "c cl", i.e. chord * section cl.
    c_cl = vals[6]

    if chord != 0:
        cl_section = c_cl / chord
    else:
        cl_section = 0.0

    lift_per_span = q * c_cl

    rows.append({
        "strip_id": j,
        "y_m": abs(y),
        "chord_m": chord,
        "c_cl_m": c_cl,
        "cl_section": cl_section,
        "lift_per_span_Npm": lift_per_span
    })

if not rows:
    raise RuntimeError("No strip-force rows parsed. Open the FS file and check the table format.")

# Sort by positive half-span coordinate
rows = sorted(rows, key=lambda r: r["y_m"])

# If AVL includes both left and right wings, average duplicate absolute y stations.
grouped = {}
for r in rows:
    key = round(r["y_m"], 6)
    grouped.setdefault(key, []).append(r)

avg_rows = []
for key, group in grouped.items():
    avg_rows.append({
        "y_m": sum(r["y_m"] for r in group) / len(group),
        "cl_section": sum(r["cl_section"] for r in group) / len(group),
        "lift_per_span_Npm": sum(r["lift_per_span_Npm"] for r in group) / len(group)
    })

avg_rows = sorted(avg_rows, key=lambda r: r["y_m"])

out_file = output_dir / "avl_spanload_alpha4.csv"

with out_file.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["y_m", "cl_section", "lift_per_span_Npm"])
    writer.writeheader()
    writer.writerows(avg_rows)

print(f"Wrote {out_file}")
print(f"Parsed {len(rows)} strip rows, reduced to {len(avg_rows)} positive half-span stations.")
print("First few rows:")
for r in avg_rows[:5]:
    print(r)
