# Phase 7 AVL Validation Run Notes

Geometry file expected:

```text
outputs/avl/electric_uav_wing.avl
```

## Manual run

From the project root:

```powershell
avl outputs/avl/electric_uav_wing.avl
```

Then inside AVL, use `OPER`, set angle of attack cases, execute, and export results.

A command template has been generated here:

```text
outputs/avl_validation/avl_manual_command_template.txt
```

Because AVL installations can differ, treat this as a starting command script. If automatic redirection works on your machine, try:

```powershell
avl < outputs/avl_validation/avl_manual_command_template.txt
```

## What to collect

1. Alpha sweep table:
   - alpha [deg]
   - CL
   - CDi
   - CM

2. Spanwise strip-load file at alpha = 4.0 deg.

## Save manual CSV for MATLAB comparison

Create this CSV manually if automatic parsing is difficult:

```text
outputs/avl_validation/manual_exports/avl_spanload_alpha4.csv
```

Required columns:

```text
y_m,cl_section,lift_per_span_Npm
```

If you do not have `lift_per_span_Npm`, provide `y_m` and `cl_section`; MATLAB can still compare normalized spanload shape after you enter total lift.
