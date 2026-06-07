function Lprime = build_elliptic_lift_distribution(y, totalHalfWingLift_N)
% build_elliptic_lift_distribution  Elliptic lift per unit span for a half wing.
%
% Integral from 0 to L of Lprime(y) dy = totalHalfWingLift_N.
% Lprime(y) = A * sqrt(1 - (y/L)^2), where A = 4*L_half/(pi*L).

    y = y(:);
    L = max(y);

    if L <= 0
        error('Half-span must be positive.');
    end

    shape = sqrt(max(0, 1 - (y ./ L).^2));
    areaShape = trapz(y, shape);

    if areaShape <= 0
        error('Invalid elliptic lift shape area.');
    end

    Lprime = totalHalfWingLift_N * shape ./ areaShape;
end
