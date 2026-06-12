# Composite Aeroelastic Tailoring Project — Results Summary

## Main conclusion

The best balanced layup candidate is **tailored_30**. It provides useful passive washout, good bending stiffness, acceptable deflection, and strong divergence/flutter margins. The **tailored_20** layup gives the lowest deflection, but with lower torsional/divergence margin. The **torsion_stiff** layup has strong torsional behavior but excessive bending deflection.

## Elliptic-load static aeroelastic results

| Name               |   TipDeflection_mm |   TipTwistTotal_deg |
|:-------------------|-------------------:|--------------------:|
| baseline_quasi_iso |            47.1934 |         -0.00988008 |
| axial_stiff        |            32.0216 |          0.0318919  |
| torsion_stiff      |           139.917  |         -0.140924   |
| tailored_30        |            33.8528 |         -0.1067     |
| tailored_20        |            21.5429 |         -0.0700209  |


## Divergence results

| Name               |   V_div_mps |   V_div_over_Vcruise |   Pass_1p5x_Cruise |
|:-------------------|------------:|---------------------:|-------------------:|
| baseline_quasi_iso |     328.2   |              8.20499 |                  1 |
| axial_stiff        |     328.2   |              8.20499 |                  1 |
| torsion_stiff      |     434.154 |             10.8539  |                  1 |
| tailored_30        |     295.84  |              7.396   |                  1 |
| tailored_20        |     245.59  |              6.13974 |                  1 |


## AVL spanload-based static aeroelastic results

| layup_name                    |   TipDeflection_mm |   TipTwistTotal_deg | WashBehavior   |
|:------------------------------|-------------------:|--------------------:|:---------------|
| [0/45/-45/90/90/-45/45/0]     |           133.138  |          -0.180636  | washout        |
| [0/0/45/-45/-45/45/0/0]       |            90.3366 |          -0.0699024 | washout        |
| [45/-45/45/-45/-45/45/-45/45] |           394.723  |          -0.461833  | washout        |
| [30/-30/0/90/90/0/-30/30]     |            95.5027 |          -0.472931  | washout        |
| [20/-20/0/0/0/0/-20/20]       |            60.775  |          -0.46144   | washout        |


## OAS aerodynamic validation

|   alpha_deg |   velocity_mps |   CL_raw |   CL0_calibration |   CL_calibrated |     CD_raw | mesh_file                                   |
|------------:|---------------:|---------:|------------------:|----------------:|-----------:|:--------------------------------------------|
|           4 |             40 | 0.370679 |             0.384 |        0.754679 | 0.00319192 | outputs\oas_baseline\oas_half_wing_mesh.npy |

