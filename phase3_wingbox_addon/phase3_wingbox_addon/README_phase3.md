# Phase 3 Add-on: Wingbox EI/GJ/Kbt Trend Sweep

This add-on converts Phase 2 laminate results into a preliminary rectangular closed-wingbox stiffness model.

## Adds

```text
configs/wingbox_baseline.json
matlab/wingbox/effective_laminate_constants_from_A.m
matlab/wingbox/compute_rectangular_wingbox_stiffness.m
matlab/wingbox/run_wingbox_stiffness_sweep.m
matlab/wingbox/plot_wingbox_stiffness_sweep.m
docs/phase_3_wingbox_stiffness_theory.md
```

## Run from MATLAB

```matlab
cd('C:\CFD+FEA project\Aeroelasticity')
addpath(genpath('matlab'))
run('matlab/wingbox/run_wingbox_stiffness_sweep.m')
run('matlab/wingbox/plot_wingbox_stiffness_sweep.m')
```

## Outputs

```text
outputs/matlab/wingbox/wingbox_stiffness_summary.csv
outputs/matlab/wingbox/<layup_name>_spanwise_wingbox_stiffness.csv
```

## Important limitation

This is a preliminary engineering model. `D16/D11` is used as an early bend-twist indicator. A future phase can replace this with a full anisotropic cross-section stiffness extraction for a more rigorous `Kbt`.
