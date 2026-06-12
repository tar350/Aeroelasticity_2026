# Phase 5 — Torsional Divergence Theory

This phase estimates static torsional divergence for each layup using a first-order finite-element torsion model.

## Physical idea

Divergence is a static aeroelastic instability. If aerodynamic twist increases local angle of attack, lift increases, aerodynamic torque increases, and twist grows further. At the divergence dynamic pressure, aerodynamic stiffness cancels structural torsional stiffness.

## Simplified governing relation

For a wing torsion field theta(y), the weak-form balance is approximated as:

```text
integral(GJ theta' delta_theta' dy) = q integral(c Cl_alpha e theta delta_theta dy)
```

This gives the generalized eigenvalue problem:

```text
K_torsion theta = q_div A_aero theta
```

The lowest positive eigenvalue gives the estimated divergence dynamic pressure.

```text
V_div = sqrt(2 q_div / rho)
```

## Notes

- This is a comparative low-order estimate, not certification-grade flutter/divergence analysis.
- The aerodynamic moment arm is based on the aerodynamic center and elastic-axis offset.
- The model uses `abs(e)` by default to estimate a conservative destabilizing divergence trend.
- Higher GJ should generally increase divergence speed.
- Bend-twist coupling and wash behavior from Phase 4 should be interpreted alongside divergence speed.

## What to look for

A promising layup should have:

```text
acceptable static deflection
washout or near-neutral static twist
high enough divergence speed
reasonable GJ
reasonable EI
```

Do not choose a layup only because it maximizes divergence speed. A torsion-stiff layup can still be poor if its bending stiffness is too low.
