clear; clc; close all;

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
summaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic', 'static_aeroelastic_summary.csv');

if ~isfile(summaryFile)
    error('Missing static aeroelastic summary file. Run run_static_aeroelastic_sweep.m first.');
end

T = readtable(summaryFile);
labels = categorical(string(T.Name));

figure;
bar(labels, T.TipDeflection_mm);
ylabel('Tip deflection [mm]');
title('Static Aeroelastic Tip Deflection by Layup');
grid on;

figure;
bar(labels, T.TipTwistTotal_deg);
ylabel('Tip twist [deg]');
title('Total Static Tip Twist by Layup');
yline(0, '--');
grid on;

figure;
bar(labels, T.TipTwistAero_deg);
ylabel('Aero torque contribution [deg]');
title('Aerodynamic Torque Contribution to Tip Twist');
yline(0, '--');
grid on;

figure;
bar(labels, T.TipTwistCoupling_deg);
ylabel('Bend-twist contribution [deg]');
title('Bend-Twist Coupling Contribution to Tip Twist');
yline(0, '--');
grid on;

figure;
bar(labels, T.RootBendingMoment_Nm);
ylabel('Root bending moment [N-m]');
title('Root Bending Moment by Layup');
grid on;

figure;
scatter(T.EI_avg_Nm2, T.GJ_avg_Nm2, 80, 'filled');
text(T.EI_avg_Nm2, T.GJ_avg_Nm2, string(T.Name), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'left');
xlabel('Average EI [N-m^2]');
ylabel('Average GJ [N-m^2]');
title('Bending vs Torsional Stiffness Trade Space');
grid on;
