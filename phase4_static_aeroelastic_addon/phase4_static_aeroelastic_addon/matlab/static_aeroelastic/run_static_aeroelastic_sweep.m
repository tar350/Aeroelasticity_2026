clear; clc;

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(projectRoot, 'matlab')));

cfgFile = fullfile(projectRoot, 'configs', 'static_aeroelastic_baseline.json');
if ~isfile(cfgFile)
    error('Missing config file: %s', cfgFile);
end
cfg = jsondecode(fileread(cfgFile));

wingboxSummaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'wingbox', 'wingbox_stiffness_summary.csv');
if ~isfile(wingboxSummaryFile)
    error(['Missing Phase 3 wingbox summary file:\n%s\n', ...
           'Run matlab/wingbox/run_wingbox_stiffness_sweep.m first.'], wingboxSummaryFile);
end

summaryT = readtable(wingboxSummaryFile);

outDir = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

summaryOut = table();

fprintf('\nPhase 4: Static Aeroelastic Sweep\n');
fprintf('Project root: %s\n', projectRoot);
fprintf('Input: %s\n\n', wingboxSummaryFile);

for i = 1:height(summaryT)
    name = string(summaryT.Name(i));
    name = strip(name);

    if ismember('Layup', summaryT.Properties.VariableNames)
        layupStr = string(summaryT.Layup(i));
    else
        layupStr = "";
    end

    spanFile = fullfile(projectRoot, 'outputs', 'matlab', 'wingbox', char(name + "_spanwise_wingbox_stiffness.csv"));

    if isfile(spanFile)
        S = readtable(spanFile);
        vars = S.Properties.VariableNames;

        y = pick_column(S, vars, {'y_m', 'Y_m', 'span_m'});
        chord = pick_column(S, vars, {'chord_m', 'Chord_m', 'c_m'});
        EI = pick_column(S, vars, {'EI_Nm2', 'EI_span_Nm2', 'EI'});
        GJ = pick_column(S, vars, {'GJ_Nm2', 'GJ_span_Nm2', 'GJ'});
        Kbt = pick_column(S, vars, {'Kbt_indicator_Nm2', 'Kbt_indicator_span_Nm2', 'Kbt'});
    else
        % Fallback: use average/root/tip values from summary and create a smooth spanwise model.
        warning('Spanwise stiffness file not found for %s. Using summary fallback.', name);
        L = 3.0;
        y = linspace(0, L, 41)';
        chord = linspace(0.55, 0.33, numel(y))';

        EI_root = summaryT.EI_root_Nm2(i);
        EI_tip = summaryT.EI_tip_Nm2(i);
        GJ_root = summaryT.GJ_root_Nm2(i);
        GJ_tip = summaryT.GJ_tip_Nm2(i);
        Kbt_avg = summaryT.Kbt_indicator_avg_Nm2(i);

        frac = y ./ max(y);
        EI = EI_root + (EI_tip - EI_root) .* frac;
        GJ = GJ_root + (GJ_tip - GJ_root) .* frac;
        Kbt = Kbt_avg .* ones(size(y));
    end

    result = solve_static_aeroelastic_1d(y, chord, EI, GJ, Kbt, cfg);

    resultFile = fullfile(outDir, char(name + "_static_response.csv"));
    writetable(result, resultFile);

    tipDef_m = result.deflection_m(end);
    tipTwist_deg = result.thetaTotal_deg(end);
    tipAeroTwist_deg = result.thetaAero_deg(end);
    tipCouplingTwist_deg = result.thetaCoupling_deg(end);

    if tipTwist_deg > 0
        washBehavior = "wash-in";
    elseif tipTwist_deg < 0
        washBehavior = "washout";
    else
        washBehavior = "neutral";
    end

    row = table();
    row.Name = name;
    row.Layup = layupStr;
    row.RootBendingMoment_Nm = result.bendingMoment_Nm(1);
    row.RootTorque_Nm = result.torque_Nm(1);
    row.TipDeflection_m = tipDef_m;
    row.TipDeflection_mm = tipDef_m * 1000;
    row.TipTwistTotal_deg = tipTwist_deg;
    row.TipTwistAero_deg = tipAeroTwist_deg;
    row.TipTwistCoupling_deg = tipCouplingTwist_deg;
    row.WashBehavior = washBehavior;
    row.EI_avg_Nm2 = mean(result.EI_Nm2, 'omitnan');
    row.GJ_avg_Nm2 = mean(result.GJ_Nm2, 'omitnan');
    row.Kbt_indicator_avg_Nm2 = mean(result.Kbt_indicator_Nm2, 'omitnan');

    summaryOut = [summaryOut; row]; %#ok<AGROW>

    fprintf('%-20s  tip w = %+8.3f mm, tip theta = %+8.4f deg  (%s)\n', ...
        name, row.TipDeflection_mm, row.TipTwistTotal_deg, row.WashBehavior);
end

summaryOutFile = fullfile(outDir, 'static_aeroelastic_summary.csv');
writetable(summaryOut, summaryOutFile);

fprintf('\nSaved summary:\n%s\n', summaryOutFile);
fprintf('Saved individual response files in:\n%s\n\n', outDir);

function col = pick_column(T, vars, candidates)
    col = [];
    for k = 1:numel(candidates)
        idx = strcmp(vars, candidates{k});
        if any(idx)
            col = T.(vars{idx});
            col = col(:);
            return;
        end
    end
    error('Could not find any candidate column: %s', strjoin(candidates, ', '));
end
