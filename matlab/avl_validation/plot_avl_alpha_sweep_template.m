%% plot_avl_alpha_sweep_template.m
% Use this after you manually create:
% outputs/avl_validation/manual_exports/avl_alpha_sweep.csv
%
% Required columns:
% alpha_deg, CL, CDi, CM

clear; clc; close all;

projectRoot = pwd;
csvFile = fullfile(projectRoot, 'outputs', 'avl_validation', 'manual_exports', 'avl_alpha_sweep.csv');

if ~isfile(csvFile)
    error(['Missing file: ', csvFile, newline, ...
           'Create it with columns: alpha_deg, CL, CDi, CM']);
end

T = readtable(csvFile);

figure;
plot(T.alpha_deg, T.CL, 'o-', 'LineWidth', 1.5);
xlabel('\alpha [deg]');
ylabel('C_L');
title('AVL Lift Curve');
grid on;

p = polyfit(T.alpha_deg, T.CL, 1);
CLalpha_per_deg = p(1);
CLalpha_per_rad = CLalpha_per_deg * 180/pi;

fprintf('AVL CL_alpha = %.4f per deg = %.3f per rad\n', CLalpha_per_deg, CLalpha_per_rad);

figure;
plot(T.alpha_deg, T.CDi, 'o-', 'LineWidth', 1.5);
xlabel('\alpha [deg]');
ylabel('C_{D_i}');
title('AVL Induced Drag vs Angle of Attack');
grid on;

figure;
plot(T.alpha_deg, T.CM, 'o-', 'LineWidth', 1.5);
xlabel('\alpha [deg]');
ylabel('C_M');
title('AVL Pitching Moment vs Angle of Attack');
grid on;
