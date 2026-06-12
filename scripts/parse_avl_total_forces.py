import re
import csv
from pathlib import Path

project_root = Path(r"C:\CFD+FEA project\Aeroelasticity")
input_dir = project_root / "outputs" / "avl_validation"
output_dir = input_dir / "manual_exports"
output_dir.mkdir(parents=True, exist_ok=True)

rows = []

for file in sorted(input_dir.glob("*_total_forces.txt")):
    text = file.read_text(errors="ignore")

    alpha_match = re.search(r"Alpha\s*=\s*([-+0-9.Ee]+)", text)
    cl_match = re.search(r"CLtot\s*=\s*([-+0-9.Ee]+)", text)
    cdind_match = re.search(r"CDind\s*=\s*([-+0-9.Ee]+)", text)
    cm_match = re.search(r"Cmtot\s*=\s*([-+0-9.Ee]+)", text)

    if alpha_match and cl_match and cdind_match and cm_match:
        alpha = float(alpha_match.group(1))
        cl = float(cl_match.group(1))
        cdi = float(cdind_match.group(1))
        cm = float(cm_match.group(1))

        rows.append({
            "alpha_deg": alpha,
            "CL": cl,
            "CDi": cdi,
            "CM": cm,
            "source_file": file.name
        })
    else:
        print(f"Could not parse: {file.name}")

rows = sorted(rows, key=lambda r: r["alpha_deg"])

out_file = output_dir / "avl_alpha_sweep.csv"

with out_file.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["alpha_deg", "CL", "CDi", "CM", "source_file"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {out_file}")
print(f"Parsed {len(rows)} AVL total-force files.")
for r in rows:
    print(r)
