"""
Phase 10: OpenAeroStruct aerostructural baseline.

This is a coupled OAS smoke test using an isotropic-equivalent tube FEM.
It is not yet the final composite wingbox model.

Run from project root:
    python scripts/run_oas_aerostruct_baseline.py
"""

from pathlib import Path
import json
import csv
import numpy as np

import openmdao.api as om
from openaerostruct.integration.aerostruct_groups import AerostructGeometry, AerostructPoint


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAVITY = 9.80665


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


def main():
    cfg = json.loads((PROJECT_ROOT / "configs" / "oas_aerostruct_baseline.json").read_text())
    mat = cfg["tube_material"]

    mesh = build_tapered_half_mesh(
        span=cfg["span_m"],
        root_chord=cfg["root_chord_m"],
        tip_chord=cfg["tip_chord_m"],
        num_x=cfg["num_x"],
        num_y=cfg["num_y"],
    )

    n_cp = 3
    thickness_cp = np.ones(n_cp) * cfg["tube_thickness_m"]

    surface = {
        "name": "wing",
        "symmetry": cfg["symmetry"],
        "S_ref_type": cfg["S_ref_type"],
        "mesh": mesh,

        # Aero model
        # Keep OAS raw VLM CL0 at zero; AVL-derived CL0 is added only in reporting.
        "CL0": 0.0,
        "CD0": cfg["CD0"],
        "with_viscous": cfg["with_viscous"],
        "with_wave": cfg["with_wave"],
        "k_lam": 0.05,
        "t_over_c_cp": np.array([0.12]),
        "c_max_t": 0.30,

        # Structural model: first smoke test uses isotropic-equivalent tube FEM.
        "fem_model_type": "tube",
        "thickness_cp": thickness_cp,
        "twist_cp": np.zeros(3),
        "E": mat["E_Pa"],
        "G": mat["G_Pa"],
        "yield": mat["yield_Pa"],
        "safety_factor": mat["safety_factor"],
        "mrho": mat["density_kgm3"],
        "fem_origin": 0.35,
        "wing_weight_ratio": 1.0,

        # Keep this False for the first custom-geometry smoke test.
        # We can enable structural weight relief later after the baseline runs.
        "struct_weight_relief": False,
        "distributed_fuel_weight": False,
        "exact_failure_constraint": False,
    }

    print("DEBUG: Running Phase 10 OAS aerostructural baseline")
    print(f"DEBUG: tube thickness_cp = {thickness_cp}")
    print(f"DEBUG: CL0 calibration used only in reporting = {cfg['CL0_calibration']}")
    print(f"DEBUG: W0 input = {cfg['W0_N']} N = {cfg['W0_N'] / GRAVITY:.3f} kg")

    prob = om.Problem()

    indep = om.IndepVarComp()
    indep.add_output("v", val=cfg["velocity_mps"], units="m/s")
    indep.add_output("alpha", val=cfg["alpha_deg"], units="deg")
    indep.add_output("Mach_number", val=cfg["mach"])
    indep.add_output("re", val=cfg["re_per_m"], units="1/m")
    indep.add_output("rho", val=cfg["rho_kgm3"], units="kg/m**3")
    indep.add_output("CT", val=0.0, units="1/s")
    indep.add_output("R", val=1.0e6, units="m")

    # OAS expects W0 in kg, not N.
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

    # Coupled aero-structural connections.
    prob.model.connect(f"{name}.local_stiff_transformed", f"{point_name}.coupled.{name}.local_stiff_transformed")
    prob.model.connect(f"{name}.nodes", f"{point_name}.coupled.{name}.nodes")
    prob.model.connect(f"{name}.mesh", f"{point_name}.coupled.{name}.mesh")

    # Tube structural performance connections.
    prob.model.connect(f"{name}.radius", f"{com_name}.radius")
    prob.model.connect(f"{name}.thickness", f"{com_name}.thickness")
    prob.model.connect(f"{name}.nodes", f"{com_name}.nodes")
    prob.model.connect(f"{name}.t_over_c", f"{com_name}.t_over_c")

    # Total aircraft performance connections.
    prob.model.connect(f"{name}.cg_location", f"{point_name}.total_perf.{name}_cg_location")
    prob.model.connect(f"{name}.structural_mass", f"{point_name}.total_perf.{name}_structural_mass")

    prob.setup()
    prob.run_model()

    # Aero outputs.
    CL_raw_arr = safe_get(prob, f"{point_name}.{name}_perf.CL")
    CD_arr = safe_get(prob, f"{point_name}.{name}_perf.CD")

    CL_raw = float(np.ravel(CL_raw_arr)[0]) if CL_raw_arr is not None else np.nan
    CD = float(np.ravel(CD_arr)[0]) if CD_arr is not None else np.nan
    CL_calibrated = CL_raw + cfg["CL0_calibration"]

    # Structural outputs.
    structural_mass_arr = safe_get(prob, f"{name}.structural_mass")
    structural_mass_kg = float(np.ravel(structural_mass_arr)[0]) if structural_mass_arr is not None else np.nan

    def_mesh = safe_get(prob, f"{point_name}.coupled.{name}.def_mesh")
        # Debug structural displacement outputs
    disp_candidates = [
        point_name + ".coupled.wing.disp",
        point_name + ".coupled.wing.struct_states.disp",
        point_name + ".coupled.wing.def_mesh",
        point_name + ".coupled.wing.loads",
    ]

    print("\nDEBUG displacement/output candidates:")
    for cand in disp_candidates:
        val = safe_get(prob, cand)
        if val is None:
            print(f"{cand}: not found")
        else:
            arr = np.asarray(val)
            print(f"{cand}: shape={arr.shape}, min={np.min(arr):.6e}, max={np.max(arr):.6e}")

    if def_mesh is not None:
        def_mesh = np.asarray(def_mesh)

        # Positive z convention follows OAS mesh coordinates.
        # Tip deflection is mean z displacement of the tip chord line.
        tip_z_def = float(np.mean(def_mesh[:, -1, 2]))
        tip_z_undef = float(np.mean(mesh[:, -1, 2]))
        tip_deflection_m = tip_z_def - tip_z_undef
    else:
        tip_deflection_m = np.nan

    failure_arr = safe_get(prob, f"{point_name}.{name}_perf.failure")
    failure_value = float(np.ravel(failure_arr)[0]) if failure_arr is not None else np.nan

    thickness_arr = safe_get(prob, f"{name}.thickness")
    radius_arr = safe_get(prob, f"{name}.radius")

    thickness_mean_m = float(np.mean(thickness_arr)) if thickness_arr is not None else np.nan
    radius_mean_m = float(np.mean(radius_arr)) if radius_arr is not None else np.nan

    out_dir = PROJECT_ROOT / "outputs" / "oas_aerostruct_baseline"
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(
        out_dir / "oas_aerostruct_def_mesh.npy",
        np.asarray(def_mesh) if def_mesh is not None else np.array([]),
    )
    np.save(out_dir / "oas_aerostruct_undef_mesh.npy", mesh)

    summary_file = out_dir / "oas_aerostruct_baseline_summary.csv"

    with summary_file.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "alpha_deg",
                "velocity_mps",
                "CL_raw",
                "CL0_calibration",
                "CL_calibrated",
                "CD",
                "structural_mass_kg",
                "tip_deflection_m",
                "tip_deflection_mm",
                "failure_metric",
                "tube_thickness_cp_m",
                "tube_thickness_mean_m",
                "tube_radius_mean_m",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "alpha_deg": cfg["alpha_deg"],
                "velocity_mps": cfg["velocity_mps"],
                "CL_raw": CL_raw,
                "CL0_calibration": cfg["CL0_calibration"],
                "CL_calibrated": CL_calibrated,
                "CD": CD,
                "structural_mass_kg": structural_mass_kg,
                "tip_deflection_m": tip_deflection_m,
                "tip_deflection_mm": tip_deflection_m * 1000.0,
                "failure_metric": failure_value,
                "tube_thickness_cp_m": cfg["tube_thickness_m"],
                "tube_thickness_mean_m": thickness_mean_m,
                "tube_radius_mean_m": radius_mean_m,
            }
        )

    print("\nOpenAeroStruct aerostructural baseline complete.")
    print(f"Raw OAS CL         = {CL_raw:.6f}")
    print(f"Calibrated OAS CL  = {CL_calibrated:.6f}")
    print(f"OAS CD             = {CD:.6f}")
    print(f"Structural mass    = {structural_mass_kg:.6f} kg")
    print(f"Tip deflection     = {tip_deflection_m * 1000.0:.6f} mm")
    print(f"Failure metric     = {failure_value:.6f}")
    print(f"Mean tube thickness = {thickness_mean_m:.6f} m")
    print(f"Mean tube radius    = {radius_mean_m:.6f} m")
    print(f"Wrote {summary_file}")


if __name__ == "__main__":
    main()