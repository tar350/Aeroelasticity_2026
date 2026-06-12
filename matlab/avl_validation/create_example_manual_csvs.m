%% create_example_manual_csvs.m
% Creates example manual AVL CSV files with placeholder values.
% Replace these with actual AVL outputs.

clear; clc;

outDir = fullfile(pwd, 'outputs', 'avl_validation', 'manual_exports');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

alpha_deg = [-4; -2; 0; 2; 4; 6; 8; 10];
CL = 0.08 * alpha_deg + 0.25;
CDi = 0.005 + 0.035 * CL.^2;
CM = -0.05 - 0.005 * alpha_deg;

Talpha = table(alpha_deg, CL, CDi, CM);
writetable(Talpha, fullfile(outDir, 'avl_alpha_sweep.csv'));

y_m = linspace(0, 3.0, 21)';
L0 = 190;
lift_per_span_Npm = L0 * sqrt(max(0, 1 - (y_m/3.0).^2));
cl_section = lift_per_span_Npm / max(lift_per_span_Npm);

Tspan = table(y_m, cl_section, lift_per_span_Npm);
writetable(Tspan, fullfile(outDir, 'avl_spanload_alpha4.csv'));

fprintf('Created example CSVs in %s\n', outDir);
fprintf('Replace these values with real AVL exports when available.\n');
