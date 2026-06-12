function result = assemble_torsion_divergence_eigen(y, chord, GJ, cfg)
%ASSEMBLE_TORSION_DIVERGENCE_EIGEN First-order torsional divergence estimate.
%
% Governing weak-form idea:
%   integral(GJ * theta' * delta_theta' dy)
%       = q * integral(c * Cl_alpha * e * theta * delta_theta dy)
%
% This leads to the generalized eigenvalue problem:
%   K_torsion * theta = q_div * A_aero * theta
%
% Root twist is fixed: theta(0) = 0.
% Tip is free: natural torque boundary condition.
%
% This is a comparative low-order model, not certification-grade divergence.

    y = y(:);
    chord = chord(:);
    GJ = GJ(:);

    if numel(y) ~= numel(chord) || numel(y) ~= numel(GJ)
        error('y, chord, and GJ must have the same length.');
    end

    n = numel(y);
    if n < 3
        error('Need at least 3 spanwise stations for divergence eigen estimate.');
    end

    clAlpha = cfg.cl_alpha_per_rad;
    ac = cfg.aerodynamic_center_xc;
    ea = cfg.elastic_axis_xc;
    useAbs = cfg.use_absolute_moment_arm;

    K = zeros(n, n);
    A = zeros(n, n);

    for e = 1:n-1
        y1 = y(e);
        y2 = y(e+1);
        Le = y2 - y1;
        if Le <= 0
            error('Spanwise y stations must be strictly increasing.');
        end

        c_e = 0.5 * (chord(e) + chord(e+1));
        GJ_e = 0.5 * (GJ(e) + GJ(e+1));

        % Moment arm from elastic axis to aerodynamic center.
        % Dimensional arm = nondimensional chord offset * local chord.
        e_arm = (ac - ea) * c_e;
        if useAbs
            e_arm = abs(e_arm);
        end

        % Linear 2-node torsion element stiffness.
        Ke = (GJ_e / Le) * [1, -1; -1, 1];

        % Aerodynamic divergence operator per unit dynamic pressure.
        % Integral of c*Cl_alpha*e_arm*N^T*N dy for linear shape functions.
        Ae = (clAlpha * c_e * e_arm * Le / 6.0) * [2, 1; 1, 2];

        idx = [e, e+1];
        K(idx, idx) = K(idx, idx) + Ke;
        A(idx, idx) = A(idx, idx) + Ae;
    end

    % Apply root twist boundary condition theta(root) = 0 by removing root DOF.
    free = 2:n;
    Kff = K(free, free);
    Aff = A(free, free);

    % If the aerodynamic operator is nearly zero, divergence is effectively not defined.
    if rcond(Aff) < 1e-14
        qDiv = NaN;
        mode = NaN(numel(free), 1);
        eigVals = NaN;
    else
        lambda = eig(Kff, Aff);
        lambda = real(lambda(abs(imag(lambda)) < 1e-7));
        lambda = lambda(lambda > cfg.minimum_valid_qdiv_pa);
        lambda = sort(lambda);

        if isempty(lambda)
            qDiv = NaN;
            mode = NaN(numel(free), 1);
            eigVals = NaN;
        else
            qDiv = lambda(1);
            [V, D] = eig(Kff, Aff);
            d = real(diag(D));
            valid = find(abs(imag(diag(D))) < 1e-7 & d > cfg.minimum_valid_qdiv_pa);
            [~, localIdx] = min(d(valid));
            chosen = valid(localIdx);
            mode = real(V(:, chosen));
            mode = mode ./ max(abs(mode));
            eigVals = lambda;
        end
    end

    rho = cfg.rho_kgm3;
    if isnan(qDiv)
        vDiv = NaN;
    else
        vDiv = sqrt(2.0 * qDiv / rho);
    end

    thetaMode = zeros(n, 1);
    if ~all(isnan(mode))
        thetaMode(free) = mode;
    else
        thetaMode(:) = NaN;
    end

    result = struct();
    result.q_div_Pa = qDiv;
    result.V_div_mps = vDiv;
    result.theta_mode = thetaMode;
    result.eigenvalues_q_Pa = eigVals;
    result.K_matrix = K;
    result.A_matrix = A;
end
