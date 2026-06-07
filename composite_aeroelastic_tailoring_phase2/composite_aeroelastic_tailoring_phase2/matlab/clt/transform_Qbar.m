function Qbar = transform_Qbar(Q, theta_deg)
%TRANSFORM_QBAR Transform lamina stiffness matrix into laminate coordinates.
%
%   Qbar = TRANSFORM_QBAR(Q, theta_deg) returns the transformed reduced
%   stiffness matrix for a ply rotated by theta_deg from the laminate x-axis.
%
%   Positive theta follows the standard CLT convention. The laminate x-axis
%   should be chosen consistently with the physical panel direction. In this
%   project, for preliminary wing-skin CLT, x is treated as the spanwise
%   load-carrying direction unless otherwise stated.

    arguments
        Q (3,3) double
        theta_deg (1,1) double
    end

    th = deg2rad(theta_deg);
    m = cos(th);
    n = sin(th);

    Q11 = Q(1,1); Q12 = Q(1,2); Q22 = Q(2,2); Q66 = Q(3,3);

    Qb11 = Q11*m^4 + 2*(Q12 + 2*Q66)*m^2*n^2 + Q22*n^4;
    Qb22 = Q11*n^4 + 2*(Q12 + 2*Q66)*m^2*n^2 + Q22*m^4;
    Qb12 = (Q11 + Q22 - 4*Q66)*m^2*n^2 + Q12*(m^4 + n^4);
    Qb16 = (Q11 - Q12 - 2*Q66)*m^3*n - (Q22 - Q12 - 2*Q66)*m*n^3;
    Qb26 = (Q11 - Q12 - 2*Q66)*m*n^3 - (Q22 - Q12 - 2*Q66)*m^3*n;
    Qb66 = (Q11 + Q22 - 2*Q12 - 2*Q66)*m^2*n^2 + Q66*(m^4 + n^4);

    Qbar = [Qb11, Qb12, Qb16;
            Qb12, Qb22, Qb26;
            Qb16, Qb26, Qb66];
end
