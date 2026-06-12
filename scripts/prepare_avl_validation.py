"""
Phase 7 helper: prepare AVL validation files.

This script does not require AVL to be installed. It creates:
  - outputs/avl_validation/alpha_sweep_plan.csv
  - outputs/avl_validation/avl_manual_command_template.txt
  - outputs/avl_validation/README_run_avl.md
"""
from pathlib import Path
import csv
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CFG = PROJECT_ROOT / "configs" / "avl_validation_baseline.json"

def safe_case_name(alpha):
    return f"alpha_{alpha:+.1f}".replace("+", "p").replace("-", "m").replace(".", "p")

def main():
    cfg = json.loads(CFG.read_text())
    out_dir = PROJECT_ROOT / "outputs" / "avl_validation"
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_file = out_dir / "alpha_sweep_plan.csv"
    with plan_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "alpha_deg", "target_outputs"])
        for alpha in cfg["alpha_sweep_deg"]:
            writer.writerow([safe_case_name(alpha), alpha, "CL, CDi, CM, spanwise strip forces"])

    cmd_template = out_dir / "avl_manual_command_template.txt"
    lines = []
    lines.append(f"LOAD {cfg['avl_geometry_file']}")
    lines.append("OPER")
    lines.append("M")
    lines.append(f"V {cfg['velocity_mps']}")
    lines.append("")
    for alpha in cfg["alpha_sweep_deg"]:
        case_name = safe_case_name(alpha)
        lines.append(f"# Case {case_name}")
        lines.append(f"A A {alpha}")
        lines.append("X")
        lines.append(f"ST outputs/avl_validation/{case_name}_stability.txt")
        lines.append(f"FS outputs/avl_validation/{case_name}_strip_forces.txt")
        lines.append("")
    lines.append("QUIT")
    cmd_template.write_text("\n".join(lines), encoding="utf-8")

    readme = out_dir / "README_run_avl.md"
    readme.write_text(f"""# Phase 7 AVL Validation Run Notes

Geometry file expected:

```text
{cfg['avl_geometry_file']}
```

## Manual run

From the project root:

```powershell
avl {cfg['avl_geometry_file']}
```

Then inside AVL, use `OPER`, set angle of attack cases, execute, and export results.

A command template has been generated here:

```text
outputs/avl_validation/avl_manual_command_template.txt
```

Because AVL installations can differ, treat this as a starting command script. If automatic redirection works on your machine, try:

```powershell
avl < outputs/avl_validation/avl_manual_command_template.txt
```

## What to collect

1. Alpha sweep table:
   - alpha [deg]
   - CL
   - CDi
   - CM

2. Spanwise strip-load file at alpha = {cfg['reference_alpha_for_spanload_deg']} deg.

## Save manual CSV for MATLAB comparison

Create this CSV manually if automatic parsing is difficult:

```text
outputs/avl_validation/manual_exports/avl_spanload_alpha4.csv
```

Required columns:

```text
y_m,cl_section,lift_per_span_Npm
```

If you do not have `lift_per_span_Npm`, provide `y_m` and `cl_section`; MATLAB can still compare normalized spanload shape after you enter total lift.
""", encoding="utf-8")

    print(f"Created {plan_file}")
    print(f"Created {cmd_template}")
    print(f"Created {readme}")

if __name__ == "__main__":
    main()
