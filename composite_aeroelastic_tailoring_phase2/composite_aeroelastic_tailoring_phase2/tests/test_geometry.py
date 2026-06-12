from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from composite_aeroelastic.geometry import load_wing_geometry, spanwise_stations, generate_oas_half_mesh


def test_geometry_basic_values():
    wing = load_wing_geometry(REPO_ROOT / "configs" / "wing_baseline.json")
    assert wing.half_span_m == 3.0
    assert round(wing.aspect_ratio, 6) == 15.0
    assert wing.chord(0.0) == wing.root_chord_m
    assert wing.chord(wing.half_span_m) == wing.tip_chord_m


def test_station_generation():
    wing = load_wing_geometry(REPO_ROOT / "configs" / "wing_baseline.json")
    rows = spanwise_stations(wing, 5)
    assert len(rows) == 5
    assert rows[0]["eta"] == 0.0
    assert rows[-1]["eta"] == 1.0


def test_oas_mesh_shape():
    wing = load_wing_geometry(REPO_ROOT / "configs" / "wing_baseline.json")
    mesh = generate_oas_half_mesh(wing, nx=5, ny=21)
    assert mesh.shape == (5, 21, 3)
