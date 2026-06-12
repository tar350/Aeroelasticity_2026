%% Plot Phase 3 Wingbox Stiffness Sweep Results
clear; clc; close all;

script_dir = fileparts(mfilename('fullpath'));
project_root = fullfile(script_dir, '..', '..');
project_root = char(java.io.File(project_root).getCanonicalPath());

summary_file = fullfile(project_root, 'outputs', 'matlab', 'wingbox', 'wingbox_stiffness_summary.csv');
if ~exist(summary_file, 'file')
    error('Missing summary file. Run matlab/wingbox/run_wingbox_stiffness_sweep.m first.');
end

T = readtable(summary_file);
labels = categorical(T.Name);

figure;
bar(labels, T.Mass_kg);
ylabel('Half-wing wingbox mass [kg]');
title('Preliminary Wingbox Mass by Layup');
grid on;

figure;
bar(labels, T.EI_avg_Nm2);
ylabel('Average EI [N m^2]');
title('Average Bending Stiffness by Layup');
grid on;

figure;
bar(labels, T.GJ_avg_Nm2);
ylabel('Average GJ [N m^2]');
title('Average Torsional Stiffness by Layup');
grid on;

figure;
bar(labels, T.D16_D11);
ylabel('D_{16}/D_{11}');
title('Laminate-Level Bend-Twist Coupling Indicator');
grid on;

figure;
scatter(T.Mass_kg, T.GJ_avg_Nm2, 70, 'filled');
text(T.Mass_kg, T.GJ_avg_Nm2, T.Name, 'VerticalAlignment','bottom', 'HorizontalAlignment','left');
xlabel('Half-wing wingbox mass [kg]');
ylabel('Average GJ [N m^2]');
title('Mass vs Torsional Stiffness Tradeoff');
grid on;
