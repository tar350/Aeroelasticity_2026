function result = solve_static_aeroelastic_1d(y, chord, EI, GJ, Kbt_indicator, cfg)
% solve_static_aeroelastic_1d
% First-order static aeroelastic response for a half-wing cantilever.
%
% This is a low-fidelity engineering model intended for early layup ranking.
% It computes:
%   lift distribution -> shear -> bending moment -> curvature -> deflection
%   lift offset from elastic axis -> torque -> aerodynamic twist
%   bend-twist coupling indicator -> coupling-induced twist
%
% Positive theta means wash-in: local angle of attack increases.

    y = y(:);
    chord = chord(:);
    EI = EI(:);
    GJ = GJ(:);
    Kbt_indicator = Kbt_indicator(:);

    n = numel(y);
    if any([numel(chord), numel(EI), numel(GJ), numel(Kbt_indicator)] ~= n)
        error('All input vectors must have the same length.');
    end

    stiffnessFloor = cfg.minimum_stiffness_floor;
    EI = max(EI, stiffnessFloor);
    GJ = max(GJ, stiffnessFloor);

    totalHalfWingLift_N = cfg.aircraft_weight_N * cfg.load_factor / 2.0;

    switch lower(string(cfg.load_distribution))
        case "elliptic"
            Lprime = build_elliptic_lift_distribution(y, totalHalfWingLift_N);
        otherwise
            error('Unsupported load_distribution: %s', cfg.load_distribution);
    end

    % Internal shear and bending moment from tip integration.
    shear_N = cumulative_trapz_from_tip(y, Lprime);
    bendingMoment_Nm = cumulative_trapz_from_tip(y, shear_N);

    % Aerodynamic torque from lift acting away from elastic axis.
    % Positive moment arm means AC is ahead of EA and produces wash-in in this convention.
    momentArm_m = (cfg.elastic_axis_xc - cfg.aero_center_xc) .* chord;
    torquePerSpan_N = Lprime .* momentArm_m;
    torque_Nm = cumulative_trapz_from_tip(y, torquePerSpan_N);

    % Bending curvature.
    curvature_1pm = bendingMoment_Nm ./ EI;

    % Cantilever slope and deflection from root boundary conditions: w(0)=0, w'(0)=0.
    slope_rad = cumtrapz(y, curvature_1pm);
    deflection_m = cumtrapz(y, slope_rad);

    % Aerodynamic twist from torsion.
    thetaPrimeAero_1pm = torque_Nm ./ GJ;
    thetaAero_rad = cumtrapz(y, thetaPrimeAero_1pm);

    % Preliminary bend-twist coupling contribution.
    % For default cfg.coupling_twist_sign = -1, positive Kbt_indicator produces washout.
    thetaPrimeCoupling_1pm = cfg.coupling_twist_sign .* (Kbt_indicator ./ GJ) .* curvature_1pm;
    thetaCoupling_rad = cumtrapz(y, thetaPrimeCoupling_1pm);

    thetaTotal_rad = thetaAero_rad + thetaCoupling_rad;

    result = table();
    result.y_m = y;
    result.chord_m = chord;
    result.Lprime_Npm = Lprime;
    result.shear_N = shear_N;
    result.bendingMoment_Nm = bendingMoment_Nm;
    result.torque_Nm = torque_Nm;
    result.curvature_1pm = curvature_1pm;
    result.slope_rad = slope_rad;
    result.deflection_m = deflection_m;
    result.thetaAero_deg = rad2deg(thetaAero_rad);
    result.thetaCoupling_deg = rad2deg(thetaCoupling_rad);
    result.thetaTotal_deg = rad2deg(thetaTotal_rad);
    result.EI_Nm2 = EI;
    result.GJ_Nm2 = GJ;
    result.Kbt_indicator_Nm2 = Kbt_indicator;
end
