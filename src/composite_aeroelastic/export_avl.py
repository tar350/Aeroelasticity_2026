"""AVL geometry exporter for a simple trapezoidal wing.

This writes a minimal AVL geometry file with one mirrored wing surface.
It is intended for Phase 1 geometry validation, not final aerodynamic analysis.
"""

from __future__ import annotations

from pathlib import Path
from .geometry import WingGeometry


def naca_code(airfoil: str) -> str:
    airfoil = airfoil.strip().upper().replace("NACA", "")
    if not airfoil.isdigit():
        raise ValueError(f"Only simple NACA xxxx airfoils are supported in this starter exporter. Got: {airfoil}")
    return airfoil


def write_avl_file(
    wing: WingGeometry,
    output_path: str | Path,
    num_chordwise_panels: int = 8,
    num_spanwise_panels: int = 20,
    chord_spacing: float = 1.0,
    span_spacing: float = 1.0,
) -> None:
    """Write a simple AVL .avl file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sref = wing.area_m2
    cref = wing.mean_aerodynamic_chord_approx_m
    bref = wing.span_m
    xref = wing.root_chord_m * 0.25
    yref = 0.0
    zref = 0.0

    root_y = 0.0
    tip_y = wing.half_span_m

    root = {
        "x_le": wing.leading_edge_x(root_y),
        "y_le": root_y,
        "z_le": wing.dihedral_z(root_y),
        "chord": wing.chord(root_y),
        "twist": wing.twist_deg(root_y),
    }
    tip = {
        "x_le": wing.leading_edge_x(tip_y),
        "y_le": tip_y,
        "z_le": wing.dihedral_z(tip_y),
        "chord": wing.chord(tip_y),
        "twist": wing.twist_deg(tip_y),
    }
    naca = naca_code(wing.airfoil)

    text = f"""{wing.name}
# Mach
0.0
# IYsym   IZsym   Zsym
0 0 0.0
# Sref    Cref    Bref
{sref:.6f} {cref:.6f} {bref:.6f}
# Xref    Yref    Zref
{xref:.6f} {yref:.6f} {zref:.6f}
# CDp
0.0

SURFACE
Wing
# Nchord  Cspace  Nspan  Sspace
{num_chordwise_panels} {chord_spacing:.3f} {num_spanwise_panels} {span_spacing:.3f}
YDUPLICATE
0.0
ANGLE
0.0

SECTION
# Xle     Yle     Zle     Chord   Ainc
{root['x_le']:.6f} {root['y_le']:.6f} {root['z_le']:.6f} {root['chord']:.6f} {root['twist']:.6f}
NACA
{naca}

SECTION
# Xle     Yle     Zle     Chord   Ainc
{tip['x_le']:.6f} {tip['y_le']:.6f} {tip['z_le']:.6f} {tip['chord']:.6f} {tip['twist']:.6f}
NACA
{naca}
"""
    output_path.write_text(text)
