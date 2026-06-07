clear; clc; close all;

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
summaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'flutter', 'flutter_screening_summary.csv');

T = readtable(summaryFile);
labels = categorical(T.Name);
labels = reordercats(labels, string(T.Name));

figure;
bar(labels, T.f_bending_hz);
ylabel('First bending frequency [Hz]');
title('Estimated First Bending Frequency by Layup');
grid on;

figure;
bar(labels, T.f_torsion_hz);
ylabel('First torsion frequency [Hz]');
title('Estimated First Torsion Frequency by Layup');
grid on;

figure;
bar(labels, T.FrequencySeparation);
ylabel('f_{torsion} / f_{bending}');
title('Bending-Torsion Frequency Separation by Layup');
grid on;

figure;
bar(labels, T.V_flutter_screen_mps);
ylabel('Screening flutter speed [m/s]');
title('Reduced-Order Flutter Screening Speed by Layup');
grid on;

figure;
scatter(T.TipDeflection_mm, T.V_flutter_screen_mps, 80, 'filled');
text(T.TipDeflection_mm, T.V_flutter_screen_mps, T.Name, 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'left');
xlabel('Tip deflection [mm]');
ylabel('Screening flutter speed [m/s]');
title('Static Deflection vs Flutter Screening Speed');
grid on;

figure;
scatter(T.GJ_avg_Nm2, T.V_flutter_screen_mps, 80, 'filled');
text(T.GJ_avg_Nm2, T.V_flutter_screen_mps, T.Name, 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'left');
xlabel('Average torsional stiffness GJ [Nm^2]');
ylabel('Screening flutter speed [m/s]');
title('Torsional Stiffness vs Flutter Screening Speed');
grid on;
