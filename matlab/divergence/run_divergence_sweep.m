clear; clc;

projectRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
addpath(genpath(fullfile(projectRoot, 'matlab')));

cfgFile = fullfile(projectRoot, 'configs', 'divergence_baseline.json');
if ~isfile(cfgFile)
    error('Missing config file: %s', cfgFile);
end
cfg = jsondecode(fileread(cfgFile));

wingboxSummaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'wingbox', 'wingbox_stiffness_summary.csv');
if ~isfile(wingboxSummaryFile)
    error(['Missing Phase 3 wingbox summary file:\n%s\n', ...
           'Run matlab/wingbox/run_wingbox_stiffness_sweep.m first.'], wingboxSummaryFile);
end

staticSummaryFile = fullfile(projectRoot, 'outputs', 'matlab', 'static_aeroelastic', 'static_aeroelastic_summary.csv');
hasStatic = isfile(staticSummaryFile);

summaryT = readtable(wingboxSummaryFile);
if hasStatic
    staticT = readtable(staticSummaryFile);
else
    staticT = table();
    warning('Static aeroelastic summary not found. Divergence sweep will still run without wash behavior columns.');
end

outDir = fullfile(projectRoot, 'outputs', 'matlab', 'divergence');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

summaryOut = table();

fprintf('\nPhase 5: Torsional Divergence Sweep\n');
fprintf('Project root: %s\n', projectRoot);
fprintf('Input: %s\n\n', wingboxSummaryFile);

for i = 1:height(summaryT)
    name = string(summaryT.Name(i));
    name = strip(name);

    spanFile = fullfile(projectRoot, 'outputs', 'matlab', 'wingbox', char(name + "_spanwise_wingbox_stiffness.csv"));
    if ~isfile(spanFile)
        warning('Skipping %s: spanwise wingbox stiffness file not found: %s', name, spanFile);
        continue;
    end

    S = readtable(spanFile);
    vars = S.Properties.VariableNames;

    y = pick_column(S, vars, {'y_m', 'Y_m', 'span_m'});
    chord = pick_column(S, vars, {'chord_m', 'Chord_m', 'c_m'});
    GJ = pick_column(S, vars, {'GJ_Nm2', 'GJ_span_Nm2', 'GJ'});
    EI = pick_column(S, vars, {'EI_Nm2', 'EI_span_Nm2', 'EI'});
    Kbt = pick_column(S, vars, {'Kbt_indicator_Nm2', 'Kbt_indicator_span_Nm2', 'Kbt'});

    divResult = assemble_torsion_divergence_eigen(y, chord, GJ, cfg);

    modeT = table();
    modeT.y_m = y(:);
    modeT.chord_m = chord(:);
    modeT.GJ_Nm2 = GJ(:);
    modeT.theta_divergence_mode_norm = divResult.theta_mode(:);
    modeFile = fullfile(outDir, char(name + "_divergence_mode.csv"));
    writetable(modeT, modeFile);

    qCruise = 0.5 * cfg.rho_kgm3 * cfg.cruise_speed_mps^2;
    if isnan(divResult.q_div_Pa)
        qMargin = NaN;
        vMargin = NaN;
        passCruiseFactor = false;
    else
        qMargin = divResult.q_div_Pa / qCruise;
        vMargin = divResult.V_div_mps / cfg.cruise_speed_mps;
        passCruiseFactor = divResult.V_div_mps >= cfg.safety_factor_vs_cruise * cfg.cruise_speed_mps;
    end

    washBehavior = "not_available";
    tipTwistDeg = NaN;
    tipDeflectionMm = NaN;
    if hasStatic && any(strcmp(staticT.Properties.VariableNames, 'Name'))
        idxStatic = strcmp(string(staticT.Name), name);
        if any(idxStatic)
            if any(strcmp(staticT.Properties.VariableNames, 'WashBehavior'))
                washBehavior = string(staticT.WashBehavior(find(idxStatic,1)));
            end
            if any(strcmp(staticT.Properties.VariableNames, 'TipTwistTotal_deg'))
                tipTwistDeg = staticT.TipTwistTotal_deg(find(idxStatic,1));
            end
            if any(strcmp(staticT.Properties.VariableNames, 'TipDeflection_mm'))
                tipDeflectionMm = staticT.TipDeflection_mm(find(idxStatic,1));
            end
        end
    end

    row = table();
    row.Name = name;
    if ismember('Layup', summaryT.Properties.VariableNames)
        row.Layup = string(summaryT.Layup(i));
    else
        row.Layup = "";
    end
    row.q_div_Pa = divResult.q_div_Pa;
    row.V_div_mps = divResult.V_div_mps;
    row.V_div_over_Vcruise = vMargin;
    row.q_div_over_qcruise = qMargin;
    row.Pass_1p5x_Cruise = passCruiseFactor;
    row.WashBehavior = washBehavior;
    row.TipTwistTotal_deg = tipTwistDeg;
    row.TipDeflection_mm = tipDeflectionMm;
    row.EI_avg_Nm2 = mean(EI, 'omitnan');
    row.GJ_avg_Nm2 = mean(GJ, 'omitnan');
    row.Kbt_indicator_avg_Nm2 = mean(Kbt, 'omitnan');

    summaryOut = [summaryOut; row]; %#ok<AGROW>

    fprintf('%-20s  Vdiv = %8.2f m/s  Vdiv/Vcruise = %6.2f  pass=%d  wash=%s\n', ...
        name, row.V_div_mps, row.V_div_over_Vcruise, row.Pass_1p5x_Cruise, row.WashBehavior);
end

summaryOutFile = fullfile(outDir, 'divergence_summary.csv');
writetable(summaryOut, summaryOutFile);

fprintf('\nSaved divergence summary:\n%s\n', summaryOutFile);
fprintf('Saved individual divergence modes in:\n%s\n\n', outDir);

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
