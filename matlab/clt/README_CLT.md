# MATLAB CLT Module — Phase 2

This folder implements Classical Laminate Theory for preliminary composite layup screening.

## Coordinate convention

For the first project version, the laminate `x` direction is treated as the main wing-skin load-carrying direction. For a wing skin panel, this is usually aligned with the spanwise direction when studying bending stiffness contribution. Keep this convention consistent when interpreting `0°`, `±45°`, and `90°` plies.

## Run

From MATLAB:

```matlab
cd matlab/clt
run_layup_sweep
```

The script may also be run from the project root using:

```matlab
run('matlab/clt/run_layup_sweep.m')
```

## Outputs

- `outputs/matlab/clt_layup_summary.csv`
- `outputs/matlab/abd/<layup_name>_ABD.mat`

## Interpretation

- `A` matrix: extensional stiffness, units N/m
- `B` matrix: bending-extension coupling, units N
- `D` matrix: bending stiffness, units N*m
- `D16/D11`, `D26/D22`: first screening indicators for bending/twisting coupling tendency at laminate level

These are laminate-level metrics only. In Phase 3, the laminate stiffnesses will be mapped into equivalent wingbox beam properties: `EI`, `GJ`, and `Kbt`.
