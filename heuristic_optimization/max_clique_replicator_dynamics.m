% returns the max clique size and the correspoding vector representing the 
% clique

function [x, max_clique_size] = max_clique_replicator_dynamics(A, num_iterations)
    [m,m] = size(A);
    for k = 1: num_iterations   
        % initializing the variables 
        x = rand(10,1)/m;
        x_new = x;
        fitness = get_fitness(x, A);
        max_fitness = fitness;
        
        while true
            % updating x 
            for i = 1 : m
                factor = ( A(i,:) * x / (x' * A * x) );
                x_new(i) = x(i) * factor;
            end
            
            diff = abs(max(x - x_new));
            % checking the diff between present and previous
            % vectors
            if  diff < 2 * eps
                break;            
            end
            x = x_new;
        fitness = get_fitness(x, A);
        end
        
        if fitness > max_fitness
            max_fitness = fitness;
                   
        end
    end
    % calculating the clique size from the optimal
    % value of the cost function
    max_clique_size = 1 / (1 - 2 * max_fitness);    
end

function [fitness] = get_fitness(x, A)
	fitness = 0.5 * x' * A * x;
end


		

