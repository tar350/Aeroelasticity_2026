# Phase 1: Theory-to-output map

## Physical concept

The same half-wing geometry must be used by every later analysis module.

## Geometry variables

- `span_m`: full wingspan
- `half_span_m`: structural/aeroelastic model span
- `root_chord_m`, `tip_chord_m`: taper definition
- `sweep_LE_deg`: leading-edge sweep
- `dihedral_deg`: vertical wing angle
- `root_twist_deg`, `tip_twist_deg`: geometric twist
- `elastic_axis_xc`: structural twist axis as fraction of local chord
- `aero_center_xc`: approximate aerodynamic center as fraction of local chord

## Important physical output

The moment arm between aerodynamic center and elastic axis is:

```text
x_ac_minus_x_ea = x_ac - x_ea
```

This term becomes critical in torsional loading and divergence.

## Generated files

- `electric_uav_wing.avl`: AVL rigid aerodynamic geometry
- `electric_uav_wing_mesh.npy`: OpenAeroStruct-style custom mesh
- `spanwise_stations.csv`: MATLAB-ready geometry table
- `geometry_summary.json`: quick sanity-check values
