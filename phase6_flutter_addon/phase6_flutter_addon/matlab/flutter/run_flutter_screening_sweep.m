clear; clc;

% Phase 6: reduced-order flutter screening for composite aeroelastic tailoring.
% This phase ranks layups using first-order bending/torsion modal estimates,
% divergence margin, and static aeroelastic behavior.

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
configFile = fullfile(projectRoot, 'configs', 'flutter_baseline.json');
wingboxFile = fullfile(projectRoot, 'outputs', 'matlab', 'wingbox', 'wingbox_stiffness_summary.csv');
divergenceFile = fullfile(projectRoot, 'outputs', 'matlab', 'divergence', 'divergence_summary.csv');
staticFile = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic', 'static_aeroelastic_summary.csv');
outDir = fullfile(projectRoot, 'outputs', 'matlab', 'flutter');

if ~exist(outDir, 'dir')
    mkdir(outDir);
end

cfg = read_json_config(configFile);
W = readtable(wingboxFile);
D = readtable(divergenceFile);
S = readtable(staticFile);

n = height(W);
Name = strings(n,1);
Layup = strings(n,1);
Mass_kg = zeros(n,1);
EI_avg_Nm2 = zeros(n,1);
GJ_avg_Nm2 = zeros(n,1);
Kbt_indicator_avg_Nm2 = zeros(n,1);
TipDeflection_mm = zeros(n,1);
TipTwistTotal_deg = zeros(n,1);
WashBehavior = strings(n,1);
V_div_mps = zeros(n,1);
f_bending_hz = zeros(n,1);
f_torsion_hz = zeros(n,1);
FrequencySeparation = zeros(n,1);
V_flutter_screen_mps = zeros(n,1);
V_flutter_over_Vcruise = zeros(n,1);
Pass_1p5x_Cruise = false(n,1);
FreqFactor = zeros(n,1);
WashFactor = zeros(n,1);
DeflectionFactor = zeros(n,1);

for i = 1:n
    name = string(W.Name{i});
    idxD = find(strcmp(string(D.Name), name), 1);
    idxS = find(strcmp(string(S.Name), name), 1);

    if isempty(idxD)
        error('No divergence result found for layup: %s', name);
    end
    if isempty(idxS)
        error('No static aeroelastic result found for layup: %s', name);
    end

    out = flutter_screening_speed(W(i,:), D(idxD,:), S(idxS,:), cfg);

    Name(i) = name;
    Layup(i) = string(W.Layup{i});
    Mass_kg(i) = W.Mass_kg(i);
    EI_avg_Nm2(i) = W.EI_avg_Nm2(i);
    GJ_avg_Nm2(i) = W.GJ_avg_Nm2(i);
    Kbt_indicator_avg_Nm2(i) = W.Kbt_indicator_avg_Nm2(i);
    TipDeflection_mm(i) = S.TipDeflection_mm(idxS);
    TipTwistTotal_deg(i) = S.TipTwistTotal_deg(idxS);
    WashBehavior(i) = string(S.WashBehavior{idxS});
    V_div_mps(i) = D.V_div_mps(idxD);
    f_bending_hz(i) = out.f_bending_hz;
    f_torsion_hz(i) = out.f_torsion_hz;
    FrequencySeparation(i) = out.frequency_separation;
    V_flutter_screen_mps(i) = out.V_flutter_screen_mps;
    V_flutter_over_Vcruise(i) = out.V_flutter_over_Vcruise;
    Pass_1p5x_Cruise(i) = out.Pass_1p5x_Cruise;
    FreqFactor(i) = out.freq_factor;
    WashFactor(i) = out.wash_factor;
    DeflectionFactor(i) = out.deflection_factor;
end

T = table(Name, Layup, Mass_kg, EI_avg_Nm2, GJ_avg_Nm2, Kbt_indicator_avg_Nm2, ...
    TipDeflection_mm, TipTwistTotal_deg, WashBehavior, V_div_mps, ...
    f_bending_hz, f_torsion_hz, FrequencySeparation, ...
    V_flutter_screen_mps, V_flutter_over_Vcruise, Pass_1p5x_Cruise, ...
    FreqFactor, WashFactor, DeflectionFactor);

outFile = fullfile(outDir, 'flutter_screening_summary.csv');
writetable(T, outFile);

disp('Phase 6 flutter screening complete. Summary:');
disp(T);
fprintf('\nWrote: %s\n', outFile);

% Also write a ranked version by screening speed.
Tranked = sortrows(T, 'V_flutter_screen_mps', 'descend');
rankedFile = fullfile(outDir, 'flutter_screening_ranked.csv');
writetable(Tranked, rankedFile);
fprintf('Wrote: %s\n', rankedFile);
