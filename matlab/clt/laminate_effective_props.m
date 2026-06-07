function props = laminate_effective_props(A, h)
%LAMINATE_EFFECTIVE_PROPS Approximate in-plane laminate engineering constants.
%
%   Uses the extensional compliance matrix a = inv(A). These are preliminary
%   effective constants for laminate-level comparison, not full wingbox beam
%   properties.

    arguments
        A (3,3) double
        h (1,1) double {mustBePositive}
    end

    a = inv(A);

    props = struct();
    props.Ex = 1.0 / (a(1,1) * h);
    props.Ey = 1.0 / (a(2,2) * h);
    props.Gxy = 1.0 / (a(3,3) * h);
    props.nuxy = -a(1,2) / a(1,1);
    props.nuyx = -a(1,2) / a(2,2);
end
