# Phase 4 — First-Order Static Aeroelastic Response

This phase connects the Phase 3 wingbox stiffness results to physical wing deformation under aerodynamic loading.

## Purpose

For each layup, estimate:

- spanwise lift distribution
- shear force
- bending moment
- bending curvature
- vertical deflection
- aerodynamic torque about the elastic axis
- twist from aerodynamic torque
- twist from preliminary bend-twist coupling
- total tip twist
- wash-in or washout tendency

This is still a low-fidelity model. The goal is early layup ranking and physical interpretation, not certification-grade aeroelastic prediction.

## Structural chain

Distributed lift creates shear:

```text
V(y) = integral from y to tip of L'(s) ds
```

Shear creates bending moment:

```text
M(y) = integral from y to tip of V(s) ds
```

Bending moment creates curvature:

```text
kappa(y) = M(y) / EI(y)
```

Curvature integrates to slope and deflection:

```text
slope(y) = integral from root to y of kappa(s) ds
w(y)     = integral from root to y of slope(s) ds
```

## Torsional chain

Lift acting away from the elastic axis creates an aerodynamic torque per unit span:

```text
m_t'(y) = L'(y) * (x_EA - x_AC) * c(y)
```

Internal torque is obtained by integrating from the tip:

```text
T(y) = integral from y to tip of m_t'(s) ds
```

Twist rate from aerodynamic torque is:

```text
theta'_aero(y) = T(y) / GJ(y)
```

## Preliminary bend-twist coupling

The Phase 3 `Kbt_indicator` is used as a first-order coupling indicator:

```text
theta'_coupling(y) = sign * [Kbt_indicator(y) / GJ(y)] * kappa(y)
```

The default sign is -1, meaning positive `Kbt_indicator` produces washout under upward bending.

This sign is a convention and should be treated carefully. Later phases can replace this indicator with a more rigorous anisotropic cross-section model.

## Output interpretation

Positive twist means wash-in:

```text
positive theta -> local angle of attack increases
```

Negative twist means washout:

```text
negative theta -> local angle of attack decreases
```

A useful tailored layup generally has:

- acceptable tip deflection
- enough torsional stiffness
- total tip twist that trends toward washout
- not excessive structural mass
- sufficient margin for later divergence and flutter analysis
