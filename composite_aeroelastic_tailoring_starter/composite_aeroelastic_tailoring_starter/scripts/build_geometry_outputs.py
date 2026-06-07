from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import numpy as np

# Allow running this script from the repo root without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from composite_aeroelastic.geometry import load_wing_geometry, spanwise_stations, generate_oas_half_mesh
from composite_aeroelastic.export_avl import write_avl_file


def main() -> None:
    config_path = REPO_ROOT / "configs" / "wing_baseline.json"
    config = json.loads(config_path.read_text())
    wing = load_wing_geometry(config_path)

    n_stations = int(config["wing"]["num_spanwise_stations"])
    nx = int(config["wing"]["oas_num_chordwise_points"])
    ny = int(config["wing"]["oas_num_spanwise_points"])

    # 1) Spanwise stations for MATLAB / aeroelastic beam model
    rows = spanwise_stations(wing, n_stations)
    csv_path = REPO_ROOT / "outputs" / "matlab" / "spanwise_stations.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # 2) OAS-style custom half-wing mesh
    mesh = generate_oas_half_mesh(wing, nx=nx, ny=ny)
    mesh_path = REPO_ROOT / "outputs" / "oas_mesh" / f"{wing.name}_mesh.npy"
    mesh_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(mesh_path, mesh)

    # 3) AVL geometry file
    avl_path = REPO_ROOT / "outputs" / "avl" / f"{wing.name}.avl"
    write_avl_file(
        wing,
        avl_path,
        num_chordwise_panels=int(config["wing"]["avl_num_chordwise_panels"]),
        num_spanwise_panels=int(config["wing"]["avl_num_spanwise_panels"]),
        chord_spacing=float(config["wing"]["avl_chord_spacing"]),
        span_spacing=float(config["wing"]["avl_span_spacing"]),
    )

    # 4) Summary table
    summary = {
        "name": wing.name,
        "span_m": wing.span_m,
        "half_span_m": wing.half_span_m,
        "area_m2": wing.area_m2,
        "aspect_ratio": wing.aspect_ratio,
        "taper_ratio": wing.taper_ratio,
        "root_chord_m": wing.root_chord_m,
        "tip_chord_m": wing.tip_chord_m,
        "MAC_approx_m": wing.mean_aerodynamic_chord_approx_m,
        "elastic_axis_xc": wing.elastic_axis_xc,
        "aero_center_xc": wing.aero_center_xc,
        "ac_minus_ea_at_root_m": wing.ac_to_ea_moment_arm(0.0),
        "ac_minus_ea_at_tip_m": wing.ac_to_ea_moment_arm(wing.half_span_m),
        "oas_mesh_shape": list(mesh.shape),
        "outputs": {
            "avl": str(avl_path.relative_to(REPO_ROOT)),
            "oas_mesh": str(mesh_path.relative_to(REPO_ROOT)),
            "matlab_spanwise_csv": str(csv_path.relative_to(REPO_ROOT)),
        },
    }
    summary_path = REPO_ROOT / "outputs" / "tables" / "geometry_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("Generated Phase 1 geometry outputs:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
