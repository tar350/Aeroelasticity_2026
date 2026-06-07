# Integrated Composite Aeroelastic Tailoring Workflow

This repository is an integrated aeroelastic tailoring project for a flexible high-aspect-ratio electric/UAV wing.

## Project goal

Build a multi-tool workflow using:

1. **MATLAB** for Classical Laminate Theory and aeroelastic equations.
2. **AVL** for independent rigid aerodynamic validation.
3. **OpenAeroStruct** for future aerostructural optimization.
4. **Python** for geometry generation, orchestration, and post-processing.

## Phase 1: shared wing geometry

Phase 1 defines one baseline electric/UAV wing geometry and exports it consistently to:

1. AVL geometry file (`.avl`) for aerodynamic validation.
2. OpenAeroStruct-compatible NumPy mesh (`.npy`) for future aerostructural analysis.
3. MATLAB spanwise-station CSV for laminate/beam/aeroelastic calculations.

Run:

```bash
python scripts/build_geometry_outputs.py
```

Generated files:

```text
outputs/avl/electric_uav_wing.avl
outputs/oas_mesh/electric_uav_wing_mesh.npy
outputs/matlab/spanwise_stations.csv
outputs/tables/geometry_summary.json
```

## Phase 2: MATLAB Classical Laminate Theory

Phase 2 computes laminate stiffness for candidate composite layups:

- single-ply reduced stiffness `Q`
- transformed ply stiffness `Qbar`
- laminate `A`, `B`, and `D` matrices
- effective laminate properties
- preliminary coupling indicators such as `D16/D11` and `D26/D22`

Run in MATLAB:

```matlab
run('matlab/clt/run_layup_sweep.m')
```

Generated files:

```text
outputs/matlab/clt_layup_summary.csv
outputs/matlab/abd/<layup_name>_ABD.mat
```

## Current phases

- Phase 1: shared geometry exports — complete.
- Phase 2: MATLAB CLT layup sweep — complete.
- Phase 3: wingbox equivalent stiffness: `EI`, `GJ`, `Kbt` — next.
- Phase 4: AVL rigid aerodynamic validation.
- Phase 5: OpenAeroStruct aerostructural baseline.
- Phase 6: static aeroelastic twist/divergence.
- Phase 7: reduced-order flutter comparison.
