# Phase 9 OpenAeroStruct Baseline Add-on

Copy these files into your project root:

```text
C:\CFD+FEA project\Aeroelasticity
```

## 1. Create and activate Python environment

```powershell
cd "C:\CFD+FEA project\Aeroelasticity"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install openaerostruct
```

## 2. Check install

```powershell
python scripts\check_openaerostruct_install.py
```

## 3. Run OAS aerodynamic baseline

```powershell
python scripts\run_oas_aero_baseline.py
```

Expected output:

```text
outputs/oas_baseline/oas_aero_baseline_summary.csv
```

Compare OAS CL/CD at alpha = 4 deg against your AVL result from:

```text
outputs/avl_validation/manual_exports/avl_alpha_sweep.csv
```
