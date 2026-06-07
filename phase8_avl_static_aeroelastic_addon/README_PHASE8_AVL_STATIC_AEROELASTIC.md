# Phase 8 AVL-Based Static Aeroelastic Add-on

Copy these files into:

C:\CFD+FEA project\Aeroelasticity

Run in MATLAB:

cd('C:\CFD+FEA project\Aeroelasticity')
addpath(genpath('matlab'))

run('matlab/static_aeroelastic_avl/run_static_aeroelastic_with_avl_spanload.m')
run('matlab/static_aeroelastic_avl/plot_static_aeroelastic_with_avl_spanload.m')

Required inputs:

outputs/avl_validation/manual_exports/avl_spanload_alpha4.csv
outputs/matlab/wingbox/wingbox_stiffness_summary.csv
