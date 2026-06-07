# Integrated Composite Aeroelastic Tailoring Workflow

This starter repository is Phase 1 of the project:

**Goal:** define one baseline electric/UAV wing geometry and export it consistently to:

1. AVL geometry file (`.avl`) for aerodynamic validation.
2. OpenAeroStruct-compatible NumPy mesh (`.npy`) for future aerostructural analysis.
3. MATLAB spanwise-station CSV for laminate/beam/aeroelastic calculations.

## Why Phase 1 matters

Aeroelastic projects fail quickly when AVL, MATLAB, and OpenAeroStruct use slightly different wings. This phase creates a single source of truth for:

- Span
- Chord distribution
- Taper
- Sweep
- Dihedral
- Twist
- Elastic-axis location
- Aerodynamic-center location

## Run

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

## Next phases

- Phase 2: MATLAB Classical Laminate Theory module: Q, Qbar, A/B/D.
- Phase 3: Wingbox equivalent stiffness: EI, GJ, Kbt.
- Phase 4: AVL rigid aerodynamic validation.
- Phase 5: OpenAeroStruct aerostructural baseline.
- Phase 6: Static aeroelastic twist/divergence.
- Phase 7: Reduced-order flutter comparison.
