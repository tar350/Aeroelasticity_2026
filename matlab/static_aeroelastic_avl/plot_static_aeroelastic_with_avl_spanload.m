%% plot_static_aeroelastic_with_avl_spanload.m
clear; clc; close all;

scriptDir = fileparts(mfilename('fullpath'));
projectRoot = fileparts(fileparts(scriptDir));

summaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic_avl', 'avl_static_aeroelastic_summary.csv');
if ~isfile(summaryFile)
    error('Missing summary file. Run run_static_aeroelastic_with_avl_spanload.m first.');
end

opts = detectImportOptions(summaryFile, 'FileType', 'text', 'Delimiter', ',');
T = readtable(summaryFile, opts);

figure;
bar(categorical(T.layup_name), T.TipDeflection_mm);
ylabel('Tip deflection [mm]');
title('AVL-Based Static Aeroelastic Tip Deflection');
grid on;

figure;
bar(categorical(T.layup_name), T.TipTwistTotal_deg);
ylabel('Tip twist [deg]');
title('AVL-Based Static Aeroelastic Tip Twist');
grid on;

figure;
bar(categorical(T.layup_name), T.RootBendingMoment_Nm);
ylabel('Root bending moment [N-m]');
title('AVL-Based Root Bending Moment');
grid on;

outDir = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic_avl');

figure; hold on;
for i = 1:height(T)
    safeLayup = regexprep(string(T.layup_name(i)), '[^\w]', '_');
    f = fullfile(outDir, safeLayup + "_avl_static_response.csv");
    if isfile(f)
        R = readtable(f);
        plot(R.y_m, R.Deflection_m*1000, 'LineWidth', 1.5);
    end
end
xlabel('Spanwise location y [m]');
ylabel('Deflection [mm]');
title('AVL-Based Deflection Shape by Layup');
legend(T.layup_name, 'Interpreter', 'none', 'Location', 'best');
grid on;

figure; hold on;
for i = 1:height(T)
    safeLayup = regexprep(string(T.layup_name(i)), '[^\w]', '_');
    f = fullfile(outDir, safeLayup + "_avl_static_response.csv");
    if isfile(f)
        R = readtable(f);
        plot(R.y_m, rad2deg(R.ThetaTotal_rad), 'LineWidth', 1.5);
    end
end
xlabel('Spanwise location y [m]');
ylabel('Twist [deg]');
title('AVL-Based Twist Shape by Layup');
legend(T.layup_name, 'Interpreter', 'none', 'Location', 'best');
grid on;
