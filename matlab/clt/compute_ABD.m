function laminate = compute_ABD(layup_deg, material)
%COMPUTE_ABD Classical Laminate Theory A/B/D matrices for a layup.
%
%   laminate = COMPUTE_ABD(layup_deg, material)
%
%   layup_deg: row or column vector of ply angles in degrees, listed from
%              bottom surface to top surface of the laminate.
%
%   material fields required:
%       E1, E2, G12, nu12, ply_thickness
%
%   Output fields:
%       Q, A, B, D, ABD, h, z, Qbar_stack, layup_deg
%
%   Units:
%       A: N/m
%       B: N
%       D: N*m

    arguments
        layup_deg (:,1) double
        material struct
    end

    required = {'E1','E2','G12','nu12','ply_thickness'};
    for i = 1:numel(required)
        if ~isfield(material, required{i})
            error('Material struct missing required field: %s', required{i});
        end
    end

    nplies = numel(layup_deg);
    tply = material.ply_thickness;
    h = nplies * tply;

    % z-coordinates from bottom (-h/2) to top (+h/2)
    z = linspace(-h/2, h/2, nplies + 1);

    Q = compute_Q(material.E1, material.E2, material.G12, material.nu12);
    A = zeros(3,3);
    B = zeros(3,3);
    D = zeros(3,3);
    Qbar_stack = zeros(3,3,nplies);

    for k = 1:nplies
        Qbar = transform_Qbar(Q, layup_deg(k));
        Qbar_stack(:,:,k) = Qbar;

        z_bot = z(k);
        z_top = z(k+1);

        A = A + Qbar * (z_top - z_bot);
        B = B + 0.5 * Qbar * (z_top^2 - z_bot^2);
        D = D + (1.0/3.0) * Qbar * (z_top^3 - z_bot^3);
    end

    laminate = struct();
    laminate.layup_deg = layup_deg(:).';
    laminate.nplies = nplies;
    laminate.ply_thickness = tply;
    laminate.h = h;
    laminate.z = z;
    laminate.Q = Q;
    laminate.Qbar_stack = Qbar_stack;
    laminate.A = A;
    laminate.B = B;
    laminate.D = D;
    laminate.ABD = [A, B; B, D];
    laminate.effective = laminate_effective_props(A, h);
    laminate.coupling = laminate_coupling_metrics(A, B, D);
end
