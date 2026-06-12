function integralFromTip = cumulative_trapz_from_tip(y, f)
% cumulative_trapz_from_tip  Compute integral from station y to the wing tip.
%
% integralFromTip(i) = int_{y(i)}^{y(end)} f(s) ds
%
% This is useful for cantilever wing internal loads:
% shear(y)  = int_y^L lift(s) ds
% moment(y) = int_y^L shear(s) ds

    y = y(:);
    f = f(:);
    n = numel(y);

    if numel(f) ~= n
        error('y and f must have the same length.');
    end

    integralFromTip = zeros(n, 1);
    for i = n-1:-1:1
        dy = y(i+1) - y(i);
        integralFromTip(i) = integralFromTip(i+1) + 0.5 * (f(i) + f(i+1)) * dy;
    end
end
