clear; clc; close all;

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
summaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'divergence', 'divergence_summary.csv');

if ~isfile(summaryFile)
    error('Missing divergence summary. Run matlab/divergence/run_divergence_sweep.m first.');
end

T = readtable(summaryFile);
names = categorical(string(T.Name));

figure;
bar(names, T.V_div_mps);
ylabel('Divergence Speed V_{div} [m/s]');
title('Estimated Torsional Divergence Speed by Layup');
grid on;

figure;
bar(names, T.V_div_over_Vcruise);
ylabel('V_{div} / V_{cruise}');
title('Divergence Margin Relative to Cruise Speed');
yline(1.5, '--', '1.5x cruise target');
grid on;

figure;
scatter(T.GJ_avg_Nm2, T.V_div_mps, 90, 'filled');
text(T.GJ_avg_Nm2, T.V_div_mps, "  " + string(T.Name));
xlabel('Average GJ [N m^2]');
ylabel('Divergence Speed V_{div} [m/s]');
title('Torsional Stiffness vs Divergence Speed');
grid on;

figure;
scatter(T.TipTwistTotal_deg, T.V_div_mps, 90, 'filled');
text(T.TipTwistTotal_deg, T.V_div_mps, "  " + string(T.Name));
xlabel('Tip Twist from Static Aeroelastic Sweep [deg]');
ylabel('Divergence Speed V_{div} [m/s]');
title('Static Twist Behavior vs Divergence Speed');
grid on;
