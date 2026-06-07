function out = cumulative_trapz_from_tip_local(y, f)
% Integrates f from current station to tip.
y = y(:);
f = f(:);
n = numel(y);
out = zeros(n,1);
for i = n-1:-1:1
    dy = y(i+1) - y(i);
    out(i) = out(i+1) + 0.5*(f(i+1) + f(i))*dy;
end
end
