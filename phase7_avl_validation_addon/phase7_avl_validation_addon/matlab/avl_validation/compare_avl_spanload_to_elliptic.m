%% compare_avl_spanload_to_elliptic.m
% Compares manually exported AVL spanload to the elliptic lift assumption.
% Required manual CSV:
% outputs/avl_validation/manual_exports/avl_spanload_alpha4.csv
% Required columns: y_m, lift_per_span_Npm
% Optional: cl_section

clear; clc; close all;

projectRoot = pwd;
cfgFile = fullfile(projectRoot, 'configs', 'avl_validation_baseline.json');
cfg = jsondecode(fileread(cfgFile));

csvFile = fullfile(projectRoot, cfg.manual_avl_export_csv);
if ~isfile(csvFile)
    error(['Missing AVL manual spanload CSV: ', csvFile, newline, ...
           'Create it with columns: y_m, lift_per_span_Npm']);
end

T = readtable(csvFile);

y = T.y_m(:);
L_avl = T.lift_per_span_Npm(:);

y = abs(y);
[y, idx] = sort(y);
L_avl = L_avl(idx);

L_total_half = trapz(y, L_avl);
L0_elliptic = 4 * L_total_half / (pi * cfg.half_span_m);
L_elliptic = L0_elliptic * sqrt(max(0, 1 - (y/cfg.half_span_m).^2));

L_avl_norm = L_avl / trapz(y, L_avl);
L_ell_norm = L_elliptic / trapz(y, L_elliptic);

figure;
plot(y, L_avl, 'o-', 'LineWidth', 1.5); hold on;
plot(y, L_elliptic, '--', 'LineWidth', 1.5);
xlabel('Spanwise location y [m]');
ylabel('Lift per unit span L''(y) [N/m]');
title('AVL Spanload vs Elliptic Lift Distribution');
legend('AVL', 'Elliptic reference', 'Location', 'best');
grid on;

figure;
plot(y/cfg.half_span_m, L_avl_norm, 'o-', 'LineWidth', 1.5); hold on;
plot(y/cfg.half_span_m, L_ell_norm, '--', 'LineWidth', 1.5);
xlabel('Normalized span y/(b/2)');
ylabel('Normalized spanload shape');
title('Normalized Spanload Shape Comparison');
legend('AVL', 'Elliptic reference', 'Location', 'best');
grid on;

shape_rmse = sqrt(mean((L_avl_norm - L_ell_norm).^2));
fprintf('Half-wing lift from AVL spanload = %.3f N\n', L_total_half);
fprintf('Normalized spanload RMSE vs elliptic = %.6f\n', shape_rmse);

outDir = fullfile(projectRoot, 'outputs', 'avl_validation');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

Summary = table(L_total_half, shape_rmse, ...
    'VariableNames', {'AVL_HalfWingLift_N', 'NormalizedSpanloadRMSE_vs_Elliptic'});
writetable(Summary, fullfile(outDir, 'avl_spanload_validation_summary.csv'));
