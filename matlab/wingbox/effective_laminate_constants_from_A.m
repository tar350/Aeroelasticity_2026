function props = effective_laminate_constants_from_A(A, h)
%EFFECTIVE_LAMINATE_CONSTANTS_FROM_A Estimate effective in-plane constants from CLT A matrix.
%
% This uses the extensional compliance matrix inv(A). It is appropriate for
% preliminary laminate property comparison. Units are SI.

    a = inv(A);
    props.Ex = 1 / (a(1,1) * h);
    props.Ey = 1 / (a(2,2) * h);
    props.Gxy = 1 / (a(3,3) * h);
    props.nuxy = -a(1,2) / a(1,1);
end
