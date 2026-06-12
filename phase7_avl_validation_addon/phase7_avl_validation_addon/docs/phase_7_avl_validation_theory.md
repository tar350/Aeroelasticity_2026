# Phase 7 — AVL Baseline Aerodynamic Validation

## Purpose

The earlier static aeroelastic model used an elliptic lift distribution as a first approximation. Phase 7 introduces AVL as an independent rigid-wing aerodynamic validation step.

The goal is not yet full aeroelastic coupling. The goal is to validate the rigid aerodynamic load model before feeding more realistic spanwise loads into structural/aeroelastic analysis.

## Physical Questions

1. What is the rigid-wing lift-curve slope?
2. How does AVL's spanwise lift distribution compare to the elliptic assumption?
3. What is the induced drag trend with angle of attack?
4. Is the baseline geometry producing reasonable aerodynamic behavior before coupling to flexibility?

## Theoretical Background

For a wing at small angle of attack:

```text
C_L ≈ C_L0 + C_Lalpha * alpha
```

AVL estimates this using a vortex-lattice representation of the lifting surfaces. The primary output of interest is circulation distribution, which corresponds physically to lift per unit span:

```text
L'(y) = rho * V * Gamma(y)
```

In our first MATLAB model, we used an elliptic load:

```text
L'(y) = L0 * sqrt(1 - (y/(b/2))^2)
```

That is useful for simple theory, but a real tapered/twisted wing will not be exactly elliptic. AVL gives a more geometry-aware spanload.

## Validation Metrics

Recommended outputs:

- CL vs alpha
- CDi vs alpha
- CM vs alpha
- spanwise lift distribution
- normalized spanload RMSE between AVL and elliptic reference

## Design Use

Once AVL spanload is validated, it can replace the elliptic spanload in Phase 4 static aeroelastic calculations.
