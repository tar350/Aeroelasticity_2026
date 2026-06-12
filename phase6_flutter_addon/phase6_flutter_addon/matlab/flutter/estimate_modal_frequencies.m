function modal = estimate_modal_frequencies(EI_avg_Nm2, GJ_avg_Nm2, mass_kg, cfg)
%ESTIMATE_MODAL_FREQUENCIES First-order bending/torsion frequencies for a half-wing.
%
% This is an early-design screening model:
%   - bending: first fixed-free Euler-Bernoulli beam frequency using EI_avg
%   - torsion: first fixed-free torsion frequency using GJ_avg and polar inertia per length
%
% Inputs:
%   EI_avg_Nm2  average bending stiffness
%   GJ_avg_Nm2  average torsional stiffness
%   mass_kg     half-wing/wingbox mass used in previous phases
%   cfg         flutter_baseline.json struct
%
% Output fields:
%   f_bending_hz, f_torsion_hz, omega_bending_radps, omega_torsion_radps,
%   frequency_separation

    L = cfg.wing.half_span_m;
    c_ref = cfg.wing.reference_chord_m;
    beta1 = cfg.screening_model.beta1_cantilever_bending;
    torsion_factor = cfg.screening_model.torsion_mode_factor_fixed_free;
    r_alpha = cfg.typical_section.radius_of_gyration_chord_fraction;

    m_per_length = mass_kg / L;

    % First bending frequency for a uniform fixed-free beam.
    omega_b = beta1^2 * sqrt(EI_avg_Nm2 / (m_per_length * L^4));

    % Torsional mass polar inertia per unit span around the elastic axis.
    % r_alpha*c_ref is a first-order radius of gyration.
    I_theta_per_length = m_per_length * (r_alpha * c_ref)^2;

    % First fixed-free torsional frequency.
    omega_t = torsion_factor / L * sqrt(GJ_avg_Nm2 / I_theta_per_length);

    modal.omega_bending_radps = omega_b;
    modal.omega_torsion_radps = omega_t;
    modal.f_bending_hz = omega_b / (2*pi);
    modal.f_torsion_hz = omega_t / (2*pi);
    modal.frequency_separation = modal.f_torsion_hz / modal.f_bending_hz;
end
