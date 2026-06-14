"""
Phase 12B: OAS layup comparison using laminate-derived equivalent stiffness.

This is an equivalent-tube OpenAeroStruct comparison.
It uses Ex_GPa and Gxy_GPa from the MATLAB wingbox summary as equivalent
isotropic E and G values for each layup.

Run from project root:
    python scripts/run_oas_layup_comparison.py
"""

from pathlib import Path
import json
import csv
import re
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import openmdao.api as om
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAVITY = 9.80665


def safe_filename(text: str) -> str:
    text = str(text)
    text = re.sub(r"[^A-Za-z0-9_\\-]+", "_", text)
    return text.strip("_")


def build_tapered_half_mesh(span, root_chord, tip_chord, num_x, num_y):
    half_span = span / 2.0
    eta = np.linspace(0.0, 1.0, num_y)
    y = eta * half_span
    chord = root_chord + (tip_chord - root_chord) * eta

    mesh = np.zeros((num_x, num_y, 3))
    xsi = np.linspace(0.0, 1.0, num_x)

    for j in range(num_y):
        for i in range(num_x):
            mesh[i, j, 0] = xsi[i] * chord[j]
            mesh[i, j, 1] = y[j]
            mesh[i, j, 2] = 0.0

    return mesh


def safe_get(prob, name):
    try:
        return prob.get_val(name)
    except Exception:
        return None


def get_phase10_reference_mass():
    """
    Phase 10 OAS tube structural mass is used as a density calibration reference.
    This lets the equivalent tube mass approximately match the MATLAB wingbox mass.
    """
    path = PROJECT_ROOT / "outputs" / "oas_aerostruct_baseline" / "oas_aerostruct_baseline_summary.csv"

    if not path.exists():
        return None

    try:
        df = pd.read_csv(path)
        if "structural_mass_kg" in df.columns:
            return float(df["structural_mass_kg"].iloc[0])
    except Exception:
        return None

    return None


def run_single_layup_case(row, cfg, ref_oas_mass_kg, out_dir):
    mat = cfg["tube_material"]

    layup_name = str(row["Name"])
    layup_string = str(row["Layup"])

    equivalent_E_Pa = float(row["Ex_GPa"]) * 1.0e9
    equivalent_G_Pa = float(row["Gxy_GPa"]) * 1.0e9

    target_wingbox_mass_kg = float(row["Mass_kg"]) if "Mass_kg" in row.index else np.nan

    if ref_oas_mass_kg is not None and np.isfinite(target_wingbox_mass_kg) and ref_oas_mass_kg > 0:
        density_scale = target_wingbox_mass_kg / ref_oas_mass_kg
    else:
        density_scale = 1.0

    equivalent_density = float(mat["density_kgm3"]) * density_scale

    mesh = build_tapered_half_mesh(
        span=cfg["span_m"],
        root_chord=cfg["root_chord_m"],
        tip_chord=cfg["tip_chord_m"],
        num_x=cfg["num_x"],
        num_y=cfg["num_y"],
    )

    thickness_cp = np.ones(3) * cfg["tube_thickness_m"]

    surface = {
        "name": "wing",
        "symmetry": cfg["symmetry"],
        "S_ref_type": cfg["S_ref_type"],
        "mesh": mesh,

        # Aerodynamic model
        "CL0": 0.0,
        "CD0": cfg["CD0"],
        "with_viscous": cfg["with_viscous"],
        "with_wave": cfg["with_wave"],
        "k_lam": 0.05,
        "t_over_c_cp": np.array([0.12]),
        "c_max_t": 0.30,

        # Equivalent tube structural model
        "fem_model_type": "tube",
        "thickness_cp": thickness_cp,
        "twist_cp": np.zeros(3),

        # Layup-equivalent stiffness values
        "E": equivalent_E_Pa,
        "G": equivalent_G_Pa,

        # Use same allowable stress model as Phase 10
        "yield": mat["yield_Pa"],
        "safety_factor": mat["safety_factor"],

        # Density calibrated to MATLAB wingbox mass
        "mrho": equivalent_density,

        "fem_origin": 0.35,
        "wing_weight_ratio": 1.0,

        # Keep simple for comparison.
        # No point masses, no fuel weight, no structural weight relief.
        "struct_weight_relief": False,
        "distributed_fuel_weight": False,
        "exact_failure_constraint": False,
    }

    prob = om.Problem()

    indep = om.IndepVarComp()
    indep.add_output("v", val=cfg["velocity_mps"], units="m/s")
    indep.add_output("alpha", val=cfg["alpha_deg"], units="deg")
    indep.add_output("Mach_number", val=cfg["mach"])
    indep.add_output("re", val=cfg["re_per_m"], units="1/m")
    indep.add_output("rho", val=cfg["rho_kgm3"], units="kg/m**3")
    indep.add_output("CT", val=0.0, units="1/s")
    indep.add_output("R", val=1.0e6, units="m")
    indep.add_output("W0", val=cfg["W0_N"] / GRAVITY, units="kg")
    indep.add_output("speed_of_sound", val=cfg["speed_of_sound_mps"], units="m/s")
    indep.add_output("load_factor", val=cfg["load_factor"])
    indep.add_output("empty_cg", val=np.array(cfg["empty_cg_m"]), units="m")

    prob.model.add_subsystem("flight_vars", indep, promotes=["*"])

    name = "wing"
    point_name = "AS_point_0"
    com_name = f"{point_name}.{name}_perf"

    prob.model.add_subsystem(name, AerostructGeometry(surface=surface))

    prob.model.add_subsystem(
        point_name,
        AerostructPoint(surfaces=[surface]),
        promotes_inputs=[
            "v",
            "alpha",
            "Mach_number",
            "re",
            "rho",
            "CT",
            "R",
            "W0",
            "speed_of_sound",
            "empty_cg",
            "load_factor",
        ],
    )

    # Coupled aero-structural connections
    prob.model.connect(f"{name}.local_stiff_transformed", f"{point_name}.coupled.{name}.local_stiff_transformed")
    prob.model.connect(f"{name}.nodes", f"{point_name}.coupled.{name}.nodes")
    prob.model.connect(f"{name}.mesh", f"{point_name}.coupled.{name}.mesh")

    # Tube structural performance connections
    prob.model.connect(f"{name}.radius", f"{com_name}.radius")
    prob.model.connect(f"{name}.thickness", f"{com_name}.thickness")
    prob.model.connect(f"{name}.nodes", f"{com_name}.nodes")
    prob.model.connect(f"{name}.t_over_c", f"{com_name}.t_over_c")

    # Total aircraft performance connections
    prob.model.connect(f"{name}.cg_location", f"{point_name}.total_perf.{name}_cg_location")
    prob.model.connect(f"{name}.structural_mass", f"{point_name}.total_perf.{name}_structural_mass")

    prob.setup()
    prob.run_model()

    CL_raw_arr = safe_get(prob, f"{point_name}.{name}_perf.CL")
    CD_arr = safe_get(prob, f"{point_name}.{name}_perf.CD")
    structural_mass_arr = safe_get(prob, f"{name}.structural_mass")
    failure_arr = safe_get(prob, f"{point_name}.{name}_perf.failure")

    disp_arr = safe_get(prob, f"{point_name}.coupled.{name}.disp")
    if disp_arr is None:
        disp_arr = safe_get(prob, f"{point_name}.coupled.{name}.struct_states.disp")

    def_mesh = safe_get(prob, f"{point_name}.coupled.{name}.def_mesh")

    CL_raw = float(np.ravel(CL_raw_arr)[0]) if CL_raw_arr is not None else np.nan
    CD = float(np.ravel(CD_arr)[0]) if CD_arr is not None else np.nan
    CL_calibrated = CL_raw + float(cfg["CL0_calibration"])

    structural_mass_kg = (
        float(np.ravel(structural_mass_arr)[0])
        if structural_mass_arr is not None
        else np.nan
    )

    failure_metric = (
        float(np.ravel(failure_arr)[0])
        if failure_arr is not None
        else np.nan
    )

    if disp_arr is not None:
        disp_arr = np.asarray(disp_arr)
        z_disp = disp_arr[:, 2]

        # For the cantilever wing, the physical tip displacement is the
        # maximum absolute vertical beam displacement.
        tip_idx = int(np.argmax(np.abs(z_disp)))

        tip_deflection_m = float(z_disp[tip_idx])
        tip_deflection_abs_m = float(abs(tip_deflection_m))
        max_abs_z_deflection_m = tip_deflection_abs_m

        np.save(out_dir / f"{safe_filename(layup_name)}_disp.npy", disp_arr)
    else:
        tip_deflection_m = np.nan
        tip_deflection_abs_m = np.nan
        max_abs_z_deflection_m = np.nan

    if def_mesh is not None:
        np.save(out_dir / f"{safe_filename(layup_name)}_def_mesh.npy", np.asarray(def_mesh))

    np.save(out_dir / f"{safe_filename(layup_name)}_undef_mesh.npy", mesh)

    result = {
        "status": "success",
        "error": "",
        "Name": layup_name,
        "Layup": layup_string,
        "alpha_deg": cfg["alpha_deg"],
        "velocity_mps": cfg["velocity_mps"],
        "equivalent_E_GPa": equivalent_E_Pa / 1.0e9,
        "equivalent_G_GPa": equivalent_G_Pa / 1.0e9,
        "target_wingbox_mass_kg": target_wingbox_mass_kg,
        "density_scale": density_scale,
        "equivalent_density_kgm3": equivalent_density,
        "structural_mass_kg": structural_mass_kg,
        "CL_raw": CL_raw,
        "CL0_calibration": cfg["CL0_calibration"],
        "CL_calibrated": CL_calibrated,
        "CD": CD,
        "tip_deflection_m": tip_deflection_m,
        "tip_deflection_mm": tip_deflection_m * 1000.0,
        "tip_deflection_abs_mm": tip_deflection_abs_m * 1000.0,
        "max_abs_z_deflection_mm": max_abs_z_deflection_m * 1000.0,
        "failure_metric": failure_metric,
        "tube_thickness_m": cfg["tube_thickness_m"],
    }

    return result


def save_plots(df, out_dir):
    plot_dir = out_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    successful = df[df["status"] == "success"].copy()

    if successful.empty:
        return

    def bar_plot(y_col, ylabel, title, filename):
        if y_col not in successful.columns:
            return

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(successful["Name"].astype(str), successful[y_col])
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Layup")
        ax.tick_params(axis="x", rotation=30)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(plot_dir / filename, dpi=300)
        plt.close(fig)

    bar_plot(
        "tip_deflection_abs_mm",
        "Tip deflection magnitude [mm]",
        "OAS equivalent-tube layup comparison: tip deflection",
        "oas_layup_tip_deflection.png",
    )

    bar_plot(
        "failure_metric",
        "Failure metric",
        "OAS equivalent-tube layup comparison: failure metric",
        "oas_layup_failure_metric.png",
    )

    bar_plot(
        "CL_calibrated",
        "Calibrated CL",
        "OAS equivalent-tube layup comparison: calibrated CL",
        "oas_layup_CL.png",
    )

    bar_plot(
        "structural_mass_kg",
        "Structural mass [kg]",
        "OAS equivalent-tube layup comparison: structural mass",
        "oas_layup_structural_mass.png",
    )


def main():
    cfg_path = PROJECT_ROOT / "configs" / "oas_aerostruct_baseline.json"
    wingbox_path = PROJECT_ROOT / "outputs" / "matlab" / "wingbox" / "wingbox_stiffness_summary.csv"

    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing config: {cfg_path}")

    if not wingbox_path.exists():
        raise FileNotFoundError(f"Missing wingbox summary: {wingbox_path}")

    cfg = json.loads(cfg_path.read_text())
    wingbox_df = pd.read_csv(wingbox_path)

    required_columns = ["Name", "Layup", "Mass_kg", "Ex_GPa", "Gxy_GPa"]
    missing = [c for c in required_columns if c not in wingbox_df.columns]

    if missing:
        raise ValueError(f"Missing required columns in wingbox summary: {missing}")

    out_dir = PROJECT_ROOT / "outputs" / "oas_layup_comparison"
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_oas_mass_kg = get_phase10_reference_mass()

    print("Phase 12B: OAS layup comparison")
    print(f"Using wingbox summary: {wingbox_path}")
    print(f"Using config: {cfg_path}")

    if ref_oas_mass_kg is None:
        print("WARNING: Phase 10 reference mass not found. Density calibration scale will be 1.0.")
    else:
        print(f"Phase 10 reference OAS structural mass = {ref_oas_mass_kg:.6f} kg")

    results = []

    for _, row in wingbox_df.iterrows():
        layup_name = str(row["Name"])

        print("\n------------------------------------------------------------")
        print(f"Running OAS equivalent-tube case: {layup_name}")
        print(f"Equivalent E = {float(row['Ex_GPa']):.3f} GPa")
        print(f"Equivalent G = {float(row['Gxy_GPa']):.3f} GPa")

        try:
            result = run_single_layup_case(row, cfg, ref_oas_mass_kg, out_dir)
            print(f"Status: success")
            print(f"CL_calibrated = {result['CL_calibrated']:.6f}")
            print(f"CD = {result['CD']:.6f}")
            print(f"Structural mass = {result['structural_mass_kg']:.6f} kg")
            print(f"Tip deflection = {result['tip_deflection_mm']:.6f} mm")
            print(f"Max |z deflection| = {result['max_abs_z_deflection_mm']:.6f} mm")
            print(f"Failure metric = {result['failure_metric']:.6f}")

        except Exception as exc:
            result = {
                "status": "failed",
                "error": str(exc),
                "Name": layup_name,
                "Layup": str(row.get("Layup", "")),
                "alpha_deg": cfg.get("alpha_deg", np.nan),
                "velocity_mps": cfg.get("velocity_mps", np.nan),
                "equivalent_E_GPa": row.get("Ex_GPa", np.nan),
                "equivalent_G_GPa": row.get("Gxy_GPa", np.nan),
                "target_wingbox_mass_kg": row.get("Mass_kg", np.nan),
                "density_scale": np.nan,
                "equivalent_density_kgm3": np.nan,
                "structural_mass_kg": np.nan,
                "CL_raw": np.nan,
                "CL0_calibration": cfg.get("CL0_calibration", np.nan),
                "CL_calibrated": np.nan,
                "CD": np.nan,
                "tip_deflection_m": np.nan,
                "tip_deflection_mm": np.nan,
                "tip_deflection_abs_mm": np.nan,
                "max_abs_z_deflection_mm": np.nan,
                "failure_metric": np.nan,
                "tube_thickness_m": cfg.get("tube_thickness_m", np.nan),
            }

            print("Status: failed")
            print(exc)
            traceback.print_exc()

        results.append(result)

    summary_df = pd.DataFrame(results)

    summary_file = out_dir / "oas_layup_comparison_summary.csv"
    summary_df.to_csv(summary_file, index=False)

    save_plots(summary_df, out_dir)

    print("\n============================================================")
    print("Phase 12B complete.")
    print(f"Wrote summary: {summary_file}")
    print(f"Wrote plots to: {out_dir / 'plots'}")
    print("============================================================")


if __name__ == "__main__":
    main()
