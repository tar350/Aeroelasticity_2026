%% run_static_aeroelastic_with_avl_spanload.m
% Phase 8: use AVL spanload instead of elliptic loading.

clear; clc; close all;

scriptDir = fileparts(mfilename('fullpath'));
projectRoot = fileparts(fileparts(scriptDir));

cfgFile = fullfile(projectRoot, 'configs', 'avl_static_aeroelastic_baseline.json');
cfg = jsondecode(fileread(cfgFile));

spanloadFile = fullfile(projectRoot, cfg.avl_spanload_csv);
wingboxFile = fullfile(projectRoot, cfg.wingbox_summary_csv);

if ~isfile(spanloadFile)
    error('Missing AVL spanload CSV: %s', spanloadFile);
end
if ~isfile(wingboxFile)
    error('Missing wingbox stiffness summary: %s', wingboxFile);
end

avl = readtable(spanloadFile);
wb = readtable(wingboxFile);

requiredCols = {'y_m', 'lift_per_span_Npm'};
for k = 1:numel(requiredCols)
    if ~ismember(requiredCols{k}, avl.Properties.VariableNames)
        error('AVL spanload CSV missing required column: %s', requiredCols{k});
    end
end

y_avl = abs(avl.y_m(:));
L_avl = avl.lift_per_span_Npm(:);
[y_avl, idx] = sort(y_avl);
L_avl = L_avl(idx);

% Average duplicate left/right y stations.
[yu, ~, ic] = unique(round(y_avl, 8));
Lavg = accumarray(ic, L_avl, [], @mean);
y_avl = yu(:);
L_avl = Lavg(:);

y = linspace(0, cfg.half_span_m, cfg.spanwise_station_count)';
Lprime = interp1(y_avl, L_avl, y, 'linear', 'extrap');
Lprime(Lprime < 0) = 0;

shear = cumulative_trapz_from_tip_local(y, Lprime);
moment = cumulative_trapz_from_tip_local(y, shear);

outDir = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic_avl');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

summaryRows = table();

for i = 1:height(wb)
    layup = string(wb.layup_name(i));
    EI = wb.EI_avg_Nm2(i);
    GJ = wb.GJ_avg_Nm2(i);

    if ismember('Kbt_indicator_avg_Nm2', wb.Properties.VariableNames)
        Kbt = wb.Kbt_indicator_avg_Nm2(i);
    elseif ismember('Kbt_avg_Nm2', wb.Properties.VariableNames)
        Kbt = wb.Kbt_avg_Nm2(i);
    else
        Kbt = 0.0;
    end

    kappa = moment ./ EI;
    slope = cumtrapz(y, kappa);
    deflection = cumtrapz(y, slope);

    theta_rate_coupling = cfg.coupling_twist_sign * cfg.coupling_scale * (Kbt ./ GJ) .* kappa;
    theta_coupling = cumtrapz(y, theta_rate_coupling);
    theta_total = theta_coupling;

    tipDefl_mm = deflection(end) * 1000;
    tipTwist_deg = rad2deg(theta_total(end));
    tipTwistCoupling_deg = rad2deg(theta_coupling(end));

    if tipTwist_deg > 1e-6
        wash = "wash-in";
    elseif tipTwist_deg < -1e-6
        wash = "washout";
    else
        wash = "neutral";
    end

    rootBM = moment(1);
    halfLift = shear(1);

    response = table(y, Lprime, shear, moment, kappa, slope, deflection, theta_coupling, theta_total, ...
        'VariableNames', {'y_m','AVL_LiftPerSpan_Npm','Shear_N','BendingMoment_Nm', ...
        'Curvature_1pm','Slope_rad','Deflection_m','ThetaCoupling_rad','ThetaTotal_rad'});

    safeLayup = regexprep(layup, '[^\w]', '_');
    writetable(response, fullfile(outDir, safeLayup + "_avl_static_response.csv"));

    row = table(layup, halfLift, rootBM, tipDefl_mm, tipTwist_deg, tipTwistCoupling_deg, wash, ...
        'VariableNames', {'layup_name','AVL_HalfWingLift_N','RootBendingMoment_Nm', ...
        'TipDeflection_mm','TipTwistTotal_deg','TipTwistCoupling_deg','WashBehavior'});
    summaryRows = [summaryRows; row]; %#ok<AGROW>
end

outSummary = fullfile(outDir, 'avl_static_aeroelastic_summary.csv');
writetable(summaryRows, outSummary);

fprintf('\nAVL-based static aeroelastic summary written to:\n%s\n\n', outSummary);
disp(summaryRows);
