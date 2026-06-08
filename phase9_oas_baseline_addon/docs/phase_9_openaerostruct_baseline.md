# Phase 9 — OpenAeroStruct Baseline Integration

## Purpose

Phase 9 introduces OpenAeroStruct as the aerostructural tool in the workflow.

The first step is aerodynamic-only:

```text
project wing geometry
    ↓
OpenAeroStruct half-wing mesh
    ↓
AeroPoint solution at alpha = 4 deg
    ↓
CL/CD comparison against AVL
```

## Next phase

After this aerodynamic smoke test works, we add the aerostructural wingbox model and compare OAS structural mass/deflection against the MATLAB wingbox/static-aeroelastic estimates.
