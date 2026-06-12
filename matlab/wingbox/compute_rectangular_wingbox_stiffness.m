function station = compute_rectangular_wingbox_stiffness(chord_m, laminate, material, wingbox)
%COMPUTE_RECTANGULAR_WINGBOX_STIFFNESS Preliminary EI/GJ for a closed rectangular wingbox.
%
% Inputs:
%   chord_m  - local chord at spanwise station [m]
%   laminate - output struct from compute_ABD
%   material - material struct containing rho [kg/m^3]
%   wingbox  - wingbox config struct
%
% Outputs:
%   station struct with local geometry, EI, GJ, mass_per_length, and
%   preliminary bend-twist indicators.
%
% Assumptions:
%   - Rectangular closed thin-walled wingbox.
%   - Same laminate on skins and spar webs for this first model.
%   - Top/bottom skins dominate bending stiffness.
%   - Torsion estimated by Bredt-Batho thin-walled closed-section formula.
%   - D16/D11 and D26/D22 are laminate-level coupling indicators, not yet a
%     fully assembled anisotropic beam coupling stiffness.

    props = effective_laminate_constants_from_A(laminate.A, laminate.h);

    t_skin = laminate.h * wingbox.skin_laminate_scale;
    t_web  = laminate.h * wingbox.spar_web_laminate_scale;

    box_width = (wingbox.rear_spar_xc - wingbox.front_spar_xc) * chord_m;
    box_height = wingbox.height_to_chord_ratio * chord_m;

    if box_width <= 0 || box_height <= 0
        error('Invalid wingbox dimensions. Check spar locations and height ratio.');
    end

    % --- Bending stiffness, EI ---
    % Top and bottom skins modeled as axial caps separated by box height.
    % This is the primary bending stiffness contribution in a wingbox.
    A_skin = box_width * t_skin;
    z_skin = box_height / 2;
    I_skin_local = box_width * t_skin^3 / 12;
    EI_skins = 2 * props.Ex * (I_skin_local + A_skin * z_skin^2);

    % Add a small web bending contribution about the same bending axis.
    % For vertical spar webs, the local second moment about the horizontal
    % centroidal axis is t*h^3/12 per web.
    I_web_local = t_web * box_height^3 / 12;
    EI_webs = 2 * props.Ex * I_web_local;

    EI = EI_skins + EI_webs;

    % --- Torsional stiffness, GJ ---
    % Bredt-Batho thin-walled closed-cell formula:
    %   GJ = 4*A_m^2 / integral(ds/(G*t))
    % Rectangular box: top + bottom + front web + rear web.
    Am = box_width * box_height;
    denom = 2 * box_width / (props.Gxy * t_skin) + 2 * box_height / (props.Gxy * t_web);
    GJ = 4 * Am^2 / denom;

    % --- Preliminary laminate coupling indicators ---
    D = laminate.D;
    eps_val = 1e-12;
    D16_D11 = D(1,3) / max(abs(D(1,1)), eps_val);
    D26_D22 = D(2,3) / max(abs(D(2,2)), eps_val);

    % A practical preliminary bend-twist trend metric.
    % This is NOT a final anisotropic Kbt. It is a normalized indicator that
    % scales with bending stiffness and laminate D16 contribution.
    Kbt_indicator = EI * D16_D11;

    % --- Mass per span length ---
    perimeter_area = 2 * box_width * t_skin + 2 * box_height * t_web;
    mass_per_length = material.rho * perimeter_area;

    station = struct();
    station.chord_m = chord_m;
    station.box_width_m = box_width;
    station.box_height_m = box_height;
    station.t_skin_m = t_skin;
    station.t_web_m = t_web;
    station.Ex_Pa = props.Ex;
    station.Ey_Pa = props.Ey;
    station.Gxy_Pa = props.Gxy;
    station.EI_Nm2 = EI;
    station.GJ_Nm2 = GJ;
    station.Kbt_indicator_Nm2 = Kbt_indicator;
    station.D16_D11 = D16_D11;
    station.D26_D22 = D26_D22;
    station.mass_per_length_kgpm = mass_per_length;
end
