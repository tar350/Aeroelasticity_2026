# Phase 6 — Reduced-Order Flutter Screening Theory

This phase estimates a comparative flutter margin for each composite layup. It is intended for early design ranking only. It is not a certification-grade flutter method and should later be replaced or validated using a p-k, V-g, DLM, SHARPy, Nastran, or equivalent aeroelastic solver.

## Physical idea

Flutter is a dynamic aeroelastic instability. It occurs when unsteady aerodynamic forces feed energy into structural vibration faster than structural and aerodynamic damping remove it.

The generic aeroelastic equation is:

```text
M x_ddot + C x_dot + K x = F_a(x, x_dot, V)
```

For an early wing screening model, the most important structural quantities are:

- first bending frequency,
- first torsion frequency,
- bending-torsion frequency separation,
- torsional stiffness/divergence margin,
- static washout or wash-in behavior,
- excessive static deflection.

## Bending frequency estimate

The first bending frequency of a uniform fixed-free beam is approximated as:

```text
omega_b = beta_1^2 sqrt(EI / (m' L^4))
```

where `beta_1 = 1.875`, `EI` is average bending stiffness, `m'` is mass per unit span, and `L` is half-span.

## Torsion frequency estimate

The first torsion frequency is approximated as:

```text
omega_t = (pi / 2L) sqrt(GJ / I_theta')
```

where `GJ` is average torsional stiffness and `I_theta'` is mass polar inertia per unit span about the elastic axis.

## Screening speed

The script estimates a conservative comparative flutter screening speed using:

- divergence speed from Phase 5,
- bending/torsion frequency separation,
- washout/wash-in behavior from Phase 4,
- tip deflection penalty from Phase 4.

A layup with strong washout, adequate torsional stiffness, and good frequency separation receives a higher screening score. A layup with wash-in or excessive static deflection is penalized.

## Correct interpretation

Use the result to rank layups, not to claim a real certified flutter speed.

Good wording:

> A reduced-order flutter screening model suggests the tailored layup has stronger comparative flutter margin than the quasi-isotropic baseline.

Avoid wording:

> This layup is flutter-free up to X m/s.

The next upgrade should implement a true two-degree-of-freedom typical-section eigenvalue model or use SHARPy/Nastran/DLM for unsteady aeroelastic validation.
