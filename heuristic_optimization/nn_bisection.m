% function returns the graph bisection vector
% xbest and the corresponding cost.

function [xbest, fbest] = nn_bisection(A, initial_solution, num_temp, num_iterations, alpha)
		temp = 1;
		temp_coefficient = 0.9;
		n = length(initial_solution)/2;
        % initializing the weight matrix using the penalty as alpha
		W = A - 2* alpha + 2 * alpha * eye(2*n);
		xbest = initial_solution;
		Ebest = get_energy(xbest, W)
		for k = 1 : num_temp
            x = xbest;
            for j = 1:num_iterations
                for i = 1: 2 *n
                    % propagation function
                    x(i) = tanh((W(i,:) * x) / temp);                    		
                end
                E = get_energy(x, W);
                % if we get lower energy value
                if E < Ebest
                    % update the best solution
                    xbest = x;
                    Ebest = E;
                end

            end
            % update the temperature
            temp = temp * temp_coefficient;
        end
        % calculate the actual objective function value
		fbest = 0.25 * (sum(sum(A)) - xbest' * A * xbest);
end

% returns the energy value
function [energy] = get_energy(x, W)
    energy = - 0.5 * x' * W * x;
end
