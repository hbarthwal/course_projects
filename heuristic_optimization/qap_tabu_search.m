% Author : Himanshu Barthwal
% Quadratic Assignment Problem using Tabu Search

% Approximately solves the quadratic assignment problem
% Returns the best solution found and the cost of the 
% solution.
% a - The distance matrix
% b - The flow matrix
function [best_sol, best_cost] = qap_tabu_search(a,b, max_iter)
% initialize variables
[n,n] = size(a);
sol = randperm(n);
best_sol = sol;
best_cost = get_cost(sol, a, b);
% delta matrix helps us deciding if the current move improves the
% objective function
delta = ones(n,n) ;


A = 5 * n * n;
k = 0;
T = ceil(random('unif', .9* n , 1.1 * n));
% Z matrix acts as a tabu list
Z(1:n,1:n) = - 2* T;
break_count = 0;
while k < max_iter
    % randomly generate a tabu move u,v
    u = ceil(random('unif', 0, n));
    v = ceil(random('unif', 0, n)) ; 
    if u == v
        continue
    end
    %check if the move is tabu
    is_tabu = false;
    if (Z(u, sol(v)) + T >= k && Z(v, sol(u)) + T >= k)
        is_tabu = true;   
    end
    
    % check if the move was not taken recently
    % check if the move satisfies asipration condition
    % if any of the above holds we apply the move otherwise continue
    if ( max(Z(u, sol(v)) + A , Z(v, sol(u)) + A) <= k || (delta(u,v) <= 0) )
        is_tabu = false;
    end
    
    if is_tabu
        continue;
    end
    % update the tabu list
    Z(u,v) = k;
    
    % update the solution
    temp = sol(u);
    sol(u) = sol(v);
    sol(v) = temp;
    % now we compute the delta matrix which stores the delta values for the 
    % change in value of objective function when we take a move i,j
    for i = 1:n
        for j = 1:n            
            val1 = ( a(u,i) - a(u,j) + a(v,j) - a(v,i) );
            val2 = (b(sol(v),sol (i))  - b(sol(v), sol (j)) + b(sol(u), sol(j)) - b(sol(u),sol(i))) ;
            val3 = (a(i,u) - a(j,u) + a(j,v) - a(i,v)) ;
            val4 = (b(sol(i), sol(v)) - b(sol(j),sol(v)) + b(sol(j),sol (u)) - b(sol(i),sol(u)));
            delta(i,j) = delta(i, j) + val1 * val2 + val3 * val4;
        end
    end
    cost = get_cost(sol,a, b);
    
    if cost < best_cost
        best_sol = sol;
        best_cost = cost;
    end    
    
    k = k + 1;
end
end

% Returns the cost of a given solution
function [cost] = get_cost(sol, a, b)
n = length(sol);
cost = 0;
for i = 1 : n
    for j = 1:n
        cost = cost + a(i , j) * b(sol(i), sol(j));
    end
end
end