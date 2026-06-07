%% Phase 3: Equivalent Composite Wingbox EI/GJ/Kbt Trend Sweep
% Run this from the project root or anywhere inside MATLAB.
%
% Requires Phase 2 CLT functions in matlab/clt.

clear; clc;

script_dir = fileparts(mfilename('fullpath'));
project_root = fullfile(script_dir, '..', '..');
project_root = char(java.io.File(project_root).getCanonicalPath());

addpath(fullfile(project_root, 'matlab', 'clt'));
addpath(fullfile(project_root, 'matlab', 'wingbox'));

material_path = fullfile(project_root, 'configs', 'material_carbon_epoxy.json');
layups_path = fullfile(project_root, 'configs', 'layups.json');
wingbox_path = fullfile(project_root, 'configs', 'wingbox_baseline.json');

if ~exist(material_path, 'file'); error('Missing material config: %s', material_path); end
if ~exist(layups_path, 'file'); error('Missing layups config: %s', layups_path); end
if ~exist(wingbox_path, 'file'); error('Missing wingbox config: %s', wingbox_path); end

material = jsondecode(fileread(material_path));
layups = jsondecode(fileread(layups_path));
wingbox = jsondecode(fileread(wingbox_path));

out_dir = fullfile(project_root, 'outputs', 'matlab', 'wingbox');
fig_dir = fullfile(project_root, 'outputs', 'figures');
if ~exist(out_dir, 'dir'); mkdir(out_dir); end
if ~exist(fig_dir, 'dir'); mkdir(fig_dir); end

layup_names = fieldnames(layups);
num_layups = numel(layup_names);
Nstations = wingbox.num_spanwise_stations;

y = linspace(0, wingbox.half_span_m, Nstations).';
eta = y / wingbox.half_span_m;
chord = wingbox.root_chord_m + (wingbox.tip_chord_m - wingbox.root_chord_m) * eta;

Name = strings(num_layups,1);
Layup = strings(num_layups,1);
Mass_kg = zeros(num_layups,1);
EI_root_Nm2 = zeros(num_layups,1);
EI_tip_Nm2 = zeros(num_layups,1);
EI_avg_Nm2 = zeros(num_layups,1);
GJ_root_Nm2 = zeros(num_layups,1);
GJ_tip_Nm2 = zeros(num_layups,1);
GJ_avg_Nm2 = zeros(num_layups,1);
Kbt_indicator_avg_Nm2 = zeros(num_layups,1);
D16_D11 = zeros(num_layups,1);
D26_D22 = zeros(num_layups,1);
Ex_GPa = zeros(num_layups,1);
Gxy_GPa = zeros(num_layups,1);

fprintf('Phase 3 wingbox stiffness sweep\n');
fprintf('Wingbox: %s\n', wingbox.name);
fprintf('Half-span: %.3f m | Stations: %d\n\n', wingbox.half_span_m, Nstations);

for i = 1:num_layups
    name = layup_names{i};
    angles = double(layups.(name)(:));
    lam = compute_ABD(angles, material);

    EI = zeros(Nstations,1);
    GJ = zeros(Nstations,1);
    Kbt_ind = zeros(Nstations,1);
    mpl = zeros(Nstations,1);
    box_w = zeros(Nstations,1);
    box_h = zeros(Nstations,1);

    for j = 1:Nstations
        station = compute_rectangular_wingbox_stiffness(chord(j), lam, material, wingbox);
        EI(j) = station.EI_Nm2;
        GJ(j) = station.GJ_Nm2;
        Kbt_ind(j) = station.Kbt_indicator_Nm2;
        mpl(j) = station.mass_per_length_kgpm;
        box_w(j) = station.box_width_m;
        box_h(j) = station.box_height_m;
    end

    mass_half_wing = trapz(y, mpl);

    Name(i) = string(name);
    Layup(i) = "[" + join(string(angles.'), "/") + "]";
    Mass_kg(i) = mass_half_wing;
    EI_root_Nm2(i) = EI(1);
    EI_tip_Nm2(i) = EI(end);
    EI_avg_Nm2(i) = trapz(y, EI) / wingbox.half_span_m;
    GJ_root_Nm2(i) = GJ(1);
    GJ_tip_Nm2(i) = GJ(end);
    GJ_avg_Nm2(i) = trapz(y, GJ) / wingbox.half_span_m;
    Kbt_indicator_avg_Nm2(i) = trapz(y, Kbt_ind) / wingbox.half_span_m;
    D16_D11(i) = lam.coupling.D16_over_D11;
    D26_D22(i) = lam.coupling.D26_over_D22;
    Ex_GPa(i) = lam.effective.Ex / 1e9;
    Gxy_GPa(i) = lam.effective.Gxy / 1e9;

    span_table = table(y, eta, chord, box_w, box_h, EI, GJ, Kbt_ind, mpl, ...
        'VariableNames', {'y_m','eta','chord_m','box_width_m','box_height_m', ...
        'EI_Nm2','GJ_Nm2','Kbt_indicator_Nm2','mass_per_length_kgpm'});
    writetable(span_table, fullfile(out_dir, [name '_spanwise_wingbox_stiffness.csv']));

    fprintf('%-22s Mass=%6.3f kg | EIavg=%9.3e | GJavg=%9.3e | D16/D11=% .4f\n', ...
        name, Mass_kg(i), EI_avg_Nm2(i), GJ_avg_Nm2(i), D16_D11(i));
end

summary = table(Name, Layup, Mass_kg, Ex_GPa, Gxy_GPa, ...
    EI_root_Nm2, EI_tip_Nm2, EI_avg_Nm2, ...
    GJ_root_Nm2, GJ_tip_Nm2, GJ_avg_Nm2, ...
    Kbt_indicator_avg_Nm2, D16_D11, D26_D22);

summary_path = fullfile(out_dir, 'wingbox_stiffness_summary.csv');
writetable(summary, summary_path);

fprintf('\nWrote wingbox summary:\n%s\n', summary_path);
fprintf('Wrote spanwise stiffness tables to:\n%s\n', out_dir);
