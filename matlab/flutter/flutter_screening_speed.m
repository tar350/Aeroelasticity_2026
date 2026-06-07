function out = flutter_screening_speed(row, divergenceRow, staticRow, cfg)
%FLUTTER_SCREENING_SPEED Comparative reduced-order flutter screening estimate.
%
% This is NOT a certification-grade p-k/V-g flutter method. It is a transparent
% early-design metric to rank composite layups before building a higher-fidelity
% aeroelastic model. The estimate combines:
%   1) divergence speed/torsional stiffness margin,
%   2) bending-torsion modal separation,
%   3) static aeroelastic behavior: washout vs wash-in,
%   4) excessive static deflection penalty.
%
% It intentionally produces conservative comparative speeds below divergence.

    V_div = divergenceRow.V_div_mps;
    V_cruise = cfg.flight_condition.cruise_speed_mps;

    modal = estimate_modal_frequencies(row.EI_avg_Nm2, row.GJ_avg_Nm2, row.Mass_kg, cfg);

    freq_ref = cfg.screening_model.frequency_separation_reference;
    freq_factor = sqrt(modal.frequency_separation / freq_ref);
    freq_factor = min(cfg.screening_model.max_frequency_factor, max(cfg.screening_model.min_frequency_factor, freq_factor));

    base_fraction = cfg.screening_model.base_flutter_fraction_of_divergence;

    % Washout is beneficial; wash-in is penalized.
    tip_twist = staticRow.TipTwistTotal_deg;
    if tip_twist < 0
        wash_factor = 1.0 + cfg.screening_model.washout_bonus_max * min(abs(tip_twist)/0.12, 1.0);
    else
        wash_factor = 1.0 - cfg.screening_model.washin_penalty;
    end

    % Penalize excessive static bending deflection because low bending stiffness
    % can make the reduced-order flutter estimate misleadingly optimistic.
    defl_mm = staticRow.TipDeflection_mm;
    defl_penalty = cfg.screening_model.deflection_penalty_max * min(defl_mm / cfg.screening_model.deflection_penalty_reference_mm, 1.0);
    defl_factor = 1.0 - defl_penalty;

    V_est = V_div * base_fraction * freq_factor * wash_factor * defl_factor;

    % Keep the screening estimate below divergence.
    V_est = min(V_est, cfg.flight_condition.max_speed_factor_on_divergence * V_div);

    out.V_flutter_screen_mps = V_est;
    out.V_flutter_over_Vcruise = V_est / V_cruise;
    out.Pass_1p5x_Cruise = V_est > 1.5 * V_cruise;
    out.f_bending_hz = modal.f_bending_hz;
    out.f_torsion_hz = modal.f_torsion_hz;
    out.frequency_separation = modal.frequency_separation;
    out.freq_factor = freq_factor;
    out.wash_factor = wash_factor;
    out.deflection_factor = defl_factor;
end
