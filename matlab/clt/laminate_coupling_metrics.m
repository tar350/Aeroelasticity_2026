function metrics = laminate_coupling_metrics(A, B, D)
%LAMINATE_COUPLING_METRICS Simple normalized coupling indicators.
%
%   These are screening metrics for layup comparison. They are not yet the
%   final wingbox EI/GJ/Kbt values. In Phase 3, D and panel geometry will be
%   mapped into equivalent wingbox beam stiffness.

    metrics = struct();

    metrics.A16_over_A11 = safe_ratio(A(1,3), A(1,1)); % A16 / A11
    metrics.A26_over_A22 = safe_ratio(A(2,3), A(2,2)); % A26 / A22
    metrics.B_norm = norm(B, 'fro');
    metrics.B_over_sqrt_AD = metrics.B_norm / sqrt(max(norm(A,'fro') * norm(D,'fro'), eps));
    metrics.D16_over_D11 = safe_ratio(D(1,3), D(1,1));
    metrics.D26_over_D22 = safe_ratio(D(2,3), D(2,2));
    metrics.D66_over_D11 = safe_ratio(D(3,3), D(1,1));
end

function r = safe_ratio(num, den)
    if abs(den) < eps
        r = NaN;
    else
        r = num / den;
    end
end
