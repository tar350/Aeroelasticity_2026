# Phase 7 AVL Validation Add-on

Copy these files into the project root:

```text
C:\CFD+FEA project\Aeroelasticity
```

## Step 1 — Prepare AVL helper files

From the project root:

```powershell
python scripts/prepare_avl_validation.py
```

This creates:

```text
outputs/avl_validation/alpha_sweep_plan.csv
outputs/avl_validation/avl_manual_command_template.txt
outputs/avl_validation/README_run_avl.md
```

## Step 2 — Run AVL manually

Use the existing AVL geometry:

```text
outputs/avl/electric_uav_wing.avl
```

Collect alpha sweep values and spanload output.

## Step 3 — Create/manual-fill CSVs

Required manual files:

```text
outputs/avl_validation/manual_exports/avl_alpha_sweep.csv
outputs/avl_validation/manual_exports/avl_spanload_alpha4.csv
```

Expected columns:

```text
avl_alpha_sweep.csv:
alpha_deg, CL, CDi, CM

avl_spanload_alpha4.csv:
y_m, cl_section, lift_per_span_Npm
```

## Step 4 — Plot in MATLAB

```matlab
cd('C:\CFD+FEA project\Aeroelasticity')
addpath(genpath('matlab'))

run('matlab/avl_validation/plot_avl_alpha_sweep_template.m')
run('matlab/avl_validation/compare_avl_spanload_to_elliptic.m')
```

To create placeholder CSVs for testing the plotting scripts only:

```matlab
run('matlab/avl_validation/create_example_manual_csvs.m')
```
