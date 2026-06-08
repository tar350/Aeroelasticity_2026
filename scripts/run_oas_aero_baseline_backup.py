"""
Phase 9: OpenAeroStruct aerodynamic-only baseline.

Run:
    python scripts/run_oas_aero_baseline.py
"""

from pathlib import Path
import json
import csv
import numpy as np

import openmdao.api as om
from openaerostruct.geometry.geometry_group import Geometry
from openaerostruct.aerodynamics.aero_groups import AeroPoint


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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


def main():
    cfg = json.loads((PROJECT_ROOT / "configs" / "oas_baseline.json").read_text())

    mesh = build_tapered_half_mesh(
        span=cfg["span_m"],
        root_chord=cfg["root_chord_m"],
        tip_chord=cfg["tip_chord_m"],
        num_x=cfg["num_x"],
        num_y=cfg["num_y"],
    )

    surface = {
        "name": "wing",
        "symmetry": cfg["symmetry"],
        "S_ref_type": cfg["S_ref_type"],
        "mesh": mesh,
        "CL0": 0.0,
        "CD0": 0.0,
        "with_viscous": cfg["with_viscous"],
        "with_wave": cfg["with_wave"],
        "k_lam": 0.05,
        "t_over_c_cp": np.array([0.12]),
        "c_max_t": 0.30,
    }

    prob = om.Problem()

    indep = om.IndepVarComp()
    indep.add_output("v", val=cfg["velocity_mps"], units="m/s")
    indep.add_output("alpha", val=cfg["alpha_deg"], units="deg")
    indep.add_output("Mach_number", val=cfg["mach"])
    indep.add_output("re", val=cfg["re_per_m"], units="1/m")
    indep.add_output("rho", val=cfg["rho_kgm3"], units="kg/m**3")
    indep.add_output("cg", val=np.array(cfg["cg_m"]), units="m")

    prob.model.add_subsystem("flight_vars", indep, promotes=["*"])

    geom = Geometry(surface=surface)
    prob.model.add_subsystem("wing", geom)

    aero_point = AeroPoint(surfaces=[surface])
    point_name = "aero_point_0"
    prob.model.add_subsystem(
        point_name,
        aero_point,
        promotes_inputs=["v", "alpha", "Mach_number", "re", "rho", "cg"],
    )

    prob.model.connect("wing.mesh", point_name + ".wing.def_mesh")
    prob.model.connect("wing.mesh", point_name + ".aero_states.wing_def_mesh")

    prob.setup()
    prob.run_model()

    CL = float(prob.get_val(point_name + ".wing_perf.CL")[0])
    CD = float(prob.get_val(point_name + ".wing_perf.CD")[0])

    out_dir = PROJECT_ROOT / "outputs" / "oas_baseline"
    out_dir.mkdir(parents=True, exist_ok=True)

    mesh_file = out_dir / "oas_half_wing_mesh.npy"
    np.save(mesh_file, mesh)

    summary_file = out_dir / "oas_aero_baseline_summary.csv"
    with summary_file.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["alpha_deg", "velocity_mps", "CL", "CD", "mesh_file"],
        )
        writer.writeheader()
        writer.writerow({
            "alpha_deg": cfg["alpha_deg"],
            "velocity_mps": cfg["velocity_mps"],
            "CL": CL,
            "CD": CD,
            "mesh_file": str(mesh_file.relative_to(PROJECT_ROOT)),
        })

    print("OpenAeroStruct aerodynamic baseline complete.")
    print(f"CL = {CL:.6f}")
    print(f"CD = {CD:.6f}")
    print(f"Wrote {summary_file}")


if __name__ == "__main__":
    main()
