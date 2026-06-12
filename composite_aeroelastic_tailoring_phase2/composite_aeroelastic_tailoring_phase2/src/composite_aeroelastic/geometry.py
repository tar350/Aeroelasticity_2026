"""Geometry utilities for the composite aeroelastic tailoring project.

This module intentionally keeps the geometry simple and transparent:
- one half-wing, root at y=0 and tip at y=b/2
- linear taper
- linear twist
- constant leading-edge sweep and dihedral

Coordinate convention:
    x: chordwise, positive aft from the leading edge
    y: spanwise, positive from root to right tip
    z: vertical, positive upward
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from math import radians, tan
from pathlib import Path
from typing import Dict, List

import numpy as np


@dataclass(frozen=True)
class WingGeometry:
    name: str
    span_m: float
    area_m2: float
    root_chord_m: float
    tip_chord_m: float
    sweep_LE_deg: float
    dihedral_deg: float
    root_twist_deg: float
    tip_twist_deg: float
    airfoil: str
    elastic_axis_xc: float
    aero_center_xc: float

    @property
    def half_span_m(self) -> float:
        return self.span_m / 2.0

    @property
    def aspect_ratio(self) -> float:
        return self.span_m ** 2 / self.area_m2

    @property
    def taper_ratio(self) -> float:
        return self.tip_chord_m / self.root_chord_m

    @property
    def mean_aerodynamic_chord_approx_m(self) -> float:
        """Trapezoidal-wing MAC approximation."""
        lam = self.taper_ratio
        return (2.0 / 3.0) * self.root_chord_m * (1 + lam + lam**2) / (1 + lam)

    def chord(self, y_m: float) -> float:
        eta = y_m / self.half_span_m
        return self.root_chord_m + eta * (self.tip_chord_m - self.root_chord_m)

    def leading_edge_x(self, y_m: float) -> float:
        return y_m * tan(radians(self.sweep_LE_deg))

    def dihedral_z(self, y_m: float) -> float:
        return y_m * tan(radians(self.dihedral_deg))

    def twist_deg(self, y_m: float) -> float:
        eta = y_m / self.half_span_m
        return self.root_twist_deg + eta * (self.tip_twist_deg - self.root_twist_deg)

    def elastic_axis_x(self, y_m: float) -> float:
        return self.leading_edge_x(y_m) + self.elastic_axis_xc * self.chord(y_m)

    def aero_center_x(self, y_m: float) -> float:
        return self.leading_edge_x(y_m) + self.aero_center_xc * self.chord(y_m)

    def ac_to_ea_moment_arm(self, y_m: float) -> float:
        """Positive if aerodynamic center is aft of elastic axis."""
        return self.aero_center_x(y_m) - self.elastic_axis_x(y_m)


def load_wing_geometry(config_path: str | Path) -> WingGeometry:
    data = json.loads(Path(config_path).read_text())
    wing = data["wing"]
    aircraft = data["aircraft"]
    return WingGeometry(
        name=aircraft["name"],
        span_m=wing["span_m"],
        area_m2=wing["area_m2"],
        root_chord_m=wing["root_chord_m"],
        tip_chord_m=wing["tip_chord_m"],
        sweep_LE_deg=wing["sweep_LE_deg"],
        dihedral_deg=wing["dihedral_deg"],
        root_twist_deg=wing["root_twist_deg"],
        tip_twist_deg=wing["tip_twist_deg"],
        airfoil=wing["airfoil"],
        elastic_axis_xc=wing["elastic_axis_xc"],
        aero_center_xc=wing["aero_center_xc"],
    )


def spanwise_stations(wing: WingGeometry, n_stations: int) -> List[Dict[str, float]]:
    ys = np.linspace(0.0, wing.half_span_m, n_stations)
    rows: List[Dict[str, float]] = []
    for y in ys:
        rows.append({
            "y_m": float(y),
            "eta": float(y / wing.half_span_m),
            "x_le_m": float(wing.leading_edge_x(y)),
            "z_le_m": float(wing.dihedral_z(y)),
            "chord_m": float(wing.chord(y)),
            "twist_deg": float(wing.twist_deg(y)),
            "x_ea_m": float(wing.elastic_axis_x(y)),
            "x_ac_m": float(wing.aero_center_x(y)),
            "x_ac_minus_x_ea_m": float(wing.ac_to_ea_moment_arm(y)),
        })
    return rows


def generate_oas_half_mesh(wing: WingGeometry, nx: int, ny: int) -> np.ndarray:
    """Generate an OpenAeroStruct-style half-wing mesh array.

    OAS custom meshes are arrays with shape (num_x, num_y, 3), where num_x is
    chordwise points and num_y is spanwise points. This mesh uses the right half-wing.
    """
    y_values = np.linspace(0.0, wing.half_span_m, ny)
    xsi_values = np.linspace(0.0, 1.0, nx)  # 0 = leading edge, 1 = trailing edge
    mesh = np.zeros((nx, ny, 3))

    for j, y in enumerate(y_values):
        c = wing.chord(y)
        x_le = wing.leading_edge_x(y)
        z = wing.dihedral_z(y)
        for i, xsi in enumerate(xsi_values):
            mesh[i, j, 0] = x_le + xsi * c
            mesh[i, j, 1] = y
            mesh[i, j, 2] = z
    return mesh
