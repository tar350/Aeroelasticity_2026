# Phase 2 Theory: Classical Laminate Theory for Aeroelastic Tailoring

## Purpose

Phase 2 converts composite ply orientation into laminate stiffness. This is the first project step where aeroelastic tailoring enters physically.

The chain is:

```text
ply material properties
  ↓
single-ply reduced stiffness Q
  ↓
rotated ply stiffness Qbar
  ↓
laminate A/B/D matrices
  ↓
laminate stiffness and coupling metrics
  ↓
future wingbox EI, GJ, Kbt extraction
```

## Single ply behavior

A unidirectional composite ply is orthotropic:

- `E1`: stiffness along fiber
- `E2`: stiffness transverse to fiber
- `G12`: in-plane shear stiffness
- `nu12`: major Poisson's ratio

For carbon/epoxy, `E1` is much larger than `E2`, so ply angle strongly changes the stiffness seen by the wing.

## Reduced stiffness matrix

Under plane stress:

```text
[sigma_1 sigma_2 tau_12]^T = Q [epsilon_1 epsilon_2 gamma_12]^T
```

The local lamina stiffness `Q` is transformed into the global laminate coordinate system as `Qbar(theta)`.

## Laminate stiffness

Classical Laminate Theory gives:

```text
[N M]^T = [A B; B D] [epsilon0 kappa]^T
```

where:

- `A`: extensional stiffness
- `B`: bending-extension coupling
- `D`: bending stiffness

For symmetric laminates, `B` should be close to zero.

## Why this matters for aeroelastic tailoring

Changing ply angles changes `A`, `B`, and `D`. In later phases, these laminate-level stiffnesses are mapped into wingbox-level properties:

- `EI`: bending stiffness
- `GJ`: torsional stiffness
- `Kbt`: bending-torsion coupling stiffness

Useful aeroelastic tailoring aims to create beneficial bend-twist behavior, usually passive washout under upward bending load.

## What Phase 2 does not do yet

Phase 2 does not yet compute full wingbox `EI`, `GJ`, or flutter/divergence. It prepares the laminate stiffness data required for those phases.
