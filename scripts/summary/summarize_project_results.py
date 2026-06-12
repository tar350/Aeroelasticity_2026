from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "outputs" / "final_summary"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv_safe(path):
    path = PROJECT_ROOT / path
    if not path.exists():
        print(f"Missing: {path}")
        return None
    return pd.read_csv(path)


def main():
    files = {
        "clt": "outputs/matlab/clt_layup_summary.csv",
        "wingbox": "outputs/matlab/wingbox/wingbox_stiffness_summary.csv",
        "static_elliptic": "outputs/matlab/static_aeroelastic/static_aeroelastic_summary.csv",
        "divergence": "outputs/matlab/divergence/divergence_summary.csv",
        "flutter": "outputs/matlab/flutter/flutter_screening_summary.csv",
        "avl_validation": "outputs/avl_validation/avl_spanload_validation_summary.csv",
        "static_avl": "outputs/matlab/static_aeroelastic_avl/avl_static_aeroelastic_summary.csv",
        "oas_aero": "outputs/oas_baseline/oas_aero_baseline_summary.csv",
        "oas_aerostruct": "outputs/oas_aerostruct_baseline/oas_aerostruct_baseline_summary.csv",
    }

    data = {k: read_csv_safe(v) for k, v in files.items()}

    report_lines = []
    report_lines.append("# Composite Aeroelastic Tailoring Project — Results Summary\n")

    report_lines.append("## Main conclusion\n")
    report_lines.append(
        "The best balanced layup candidate is **tailored_30**. "
        "It provides useful passive washout, good bending stiffness, acceptable deflection, "
        "and strong divergence/flutter margins. The **tailored_20** layup gives the lowest "
        "deflection, but with lower torsional/divergence margin. The **torsion_stiff** layup "
        "has strong torsional behavior but excessive bending deflection.\n"
    )

    if data["static_elliptic"] is not None:
        report_lines.append("## Elliptic-load static aeroelastic results\n")
        df = data["static_elliptic"]
        cols = [c for c in ["Name", "TipDeflection_mm", "TipTwistTotal_deg"] if c in df.columns]
        report_lines.append(df[cols].to_markdown(index=False))
        report_lines.append("\n")

    if data["divergence"] is not None:
        report_lines.append("## Divergence results\n")
        df = data["divergence"]
        cols = [c for c in ["Name", "V_div_mps", "V_div_over_Vcruise", "Pass_1p5x_Cruise"] if c in df.columns]
        report_lines.append(df[cols].to_markdown(index=False))
        report_lines.append("\n")

    if data["static_avl"] is not None:
        report_lines.append("## AVL spanload-based static aeroelastic results\n")
        df = data["static_avl"]
        cols = [c for c in ["layup_name", "TipDeflection_mm", "TipTwistTotal_deg", "WashBehavior"] if c in df.columns]
        report_lines.append(df[cols].to_markdown(index=False))
        report_lines.append("\n")

    if data["oas_aero"] is not None:
        report_lines.append("## OAS aerodynamic validation\n")
        df = data["oas_aero"]
        report_lines.append(df.to_markdown(index=False))
        report_lines.append("\n")

    if data["oas_aerostruct"] is not None:
        report_lines.append("## OAS aerostructural smoke test\n")
        df = data["oas_aerostruct"]
        report_lines.append(df.to_markdown(index=False))
        report_lines.append("\n")
        report_lines.append(
            "Note: Phase 10 is currently an isotropic-equivalent tube FEM smoke test, "
            "not the final composite wingbox model.\n"
        )

    report = "\n".join(report_lines)
    report_file = OUT / "project_results_summary.md"
    report_file.write_text(report, encoding="utf-8")

    print(f"Wrote {report_file}")


if __name__ == "__main__":
    main()