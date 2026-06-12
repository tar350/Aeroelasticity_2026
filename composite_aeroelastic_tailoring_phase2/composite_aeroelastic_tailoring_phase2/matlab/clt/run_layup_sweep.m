%% Phase 2: Classical Laminate Theory Layup Sweep
% Run this from anywhere. The script locates the project root relative to
% this file, reads configs/material_carbon_epoxy.json and configs/layups.json,
% computes A/B/D matrices, and writes summary outputs.

clear; clc;

script_dir = fileparts(mfilename('fullpath'));
project_root = fullfile(script_dir, '..', '..');
project_root = char(java.io.File(project_root).getCanonicalPath());

addpath(script_dir);

material_path = fullfile(project_root, 'configs', 'material_carbon_epoxy.json');
layups_path = fullfile(project_root, 'configs', 'layups.json');
output_dir = fullfile(project_root, 'outputs', 'matlab');
abd_dir = fullfile(output_dir, 'abd');

if ~exist(output_dir, 'dir'); mkdir(output_dir); end
if ~exist(abd_dir, 'dir'); mkdir(abd_dir); end

material = jsondecode(fileread(material_path));
layups = jsondecode(fileread(layups_path));
layup_names = fieldnames(layups);

n = numel(layup_names);
Name = strings(n,1);
Layup = strings(n,1);
NPlies = zeros(n,1);
Thickness_m = zeros(n,1);
MassPerArea_kgm2 = zeros(n,1);
Ex_GPa = zeros(n,1);
Ey_GPa = zeros(n,1);
Gxy_GPa = zeros(n,1);
Nu_xy = zeros(n,1);
A11_Npm = zeros(n,1);
A22_Npm = zeros(n,1);
A66_Npm = zeros(n,1);
D11_Nm = zeros(n,1);
D22_Nm = zeros(n,1);
D66_Nm = zeros(n,1);
Bnorm = zeros(n,1);
B_over_sqrt_AD = zeros(n,1);
D16_over_D11 = zeros(n,1);
D26_over_D22 = zeros(n,1);
D66_over_D11 = zeros(n,1);
A16_over_A11 = zeros(n,1);
A26_over_A22 = zeros(n,1);

fprintf('Phase 2 CLT layup sweep\n');
fprintf('Material: %s\n', material.name);
fprintf('Ply thickness: %.6g m\n\n', material.ply_thickness);

for i = 1:n
    name = layup_names{i};
    angles = double(layups.(name)(:));
    lam = compute_ABD(angles, material);

    Name(i) = string(name);
    Layup(i) = "[" + join(string(angles.'), "/") + "]";
    NPlies(i) = lam.nplies;
    Thickness_m(i) = lam.h;
    MassPerArea_kgm2(i) = material.rho * lam.h;
    Ex_GPa(i) = lam.effective.Ex / 1e9;
    Ey_GPa(i) = lam.effective.Ey / 1e9;
    Gxy_GPa(i) = lam.effective.Gxy / 1e9;
    Nu_xy(i) = lam.effective.nuxy;
    A11_Npm(i) = lam.A(1,1);
    A22_Npm(i) = lam.A(2,2);
    A66_Npm(i) = lam.A(3,3);
    D11_Nm(i) = lam.D(1,1);
    D22_Nm(i) = lam.D(2,2);
    D66_Nm(i) = lam.D(3,3);
    Bnorm(i) = lam.coupling.B_norm;
    B_over_sqrt_AD(i) = lam.coupling.B_over_sqrt_AD;
    D16_over_D11(i) = lam.coupling.D16_over_D11;
    D26_over_D22(i) = lam.coupling.D26_over_D22;
    D66_over_D11(i) = lam.coupling.D66_over_D11;
    A16_over_A11(i) = lam.coupling.A16_over_A11;
    A26_over_A22(i) = lam.coupling.A26_over_A22;

    save(fullfile(abd_dir, [name '_ABD.mat']), 'lam', 'material');

    fprintf('%-22s Ex=%7.2f GPa | Gxy=%6.2f GPa | D16/D11=% .4f | D26/D22=% .4f\n', ...
        name, Ex_GPa(i), Gxy_GPa(i), D16_over_D11(i), D26_over_D22(i));
end

summary = table(Name, Layup, NPlies, Thickness_m, MassPerArea_kgm2, ...
    Ex_GPa, Ey_GPa, Gxy_GPa, Nu_xy, A11_Npm, A22_Npm, A66_Npm, ...
    D11_Nm, D22_Nm, D66_Nm, Bnorm, B_over_sqrt_AD, ...
    A16_over_A11, A26_over_A22, D16_over_D11, D26_over_D22, D66_over_D11);

summary_path = fullfile(output_dir, 'clt_layup_summary.csv');
writetable(summary, summary_path);

fprintf('\nWrote summary table:\n%s\n', summary_path);
fprintf('Wrote individual ABD .mat files to:\n%s\n', abd_dir);
