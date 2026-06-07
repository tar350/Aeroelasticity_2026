function Q = compute_Q(E1, E2, G12, nu12)
%COMPUTE_Q Reduced stiffness matrix for a unidirectional lamina.
%
%   Q = COMPUTE_Q(E1, E2, G12, nu12) returns the 3x3 reduced stiffness
%   matrix for an orthotropic lamina under plane stress.
%
%   Coordinate convention:
%     1-direction: along fiber
%     2-direction: transverse to fiber
%     12-direction: in-plane shear
%
%   Units:
%     E1, E2, G12 in Pa. Q returned in Pa.

    arguments
        E1 (1,1) double {mustBePositive}
        E2 (1,1) double {mustBePositive}
        G12 (1,1) double {mustBePositive}
        nu12 (1,1) double
    end

    nu21 = nu12 * E2 / E1;
    denom = 1.0 - nu12 * nu21;

    if denom <= 0
        error('Invalid lamina properties: 1 - nu12*nu21 must be positive.');
    end

    Q11 = E1 / denom;
    Q22 = E2 / denom;
    Q12 = nu12 * E2 / denom;
    Q66 = G12;

    Q = [Q11, Q12, 0.0;
         Q12, Q22, 0.0;
         0.0, 0.0, Q66];
end
