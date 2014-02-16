function [route, cost] = TSP2OPT(starting_city, distance_matrix)
% Calculates the minimal cost TSP 
% route using the 2OPT node exchange
% heuristic.

[m,m] = size(distance_matrix);
all_cities = (1:m);
intermediate_cities = all_cities(all_cities~=starting_city);
%display(intermediate_cities);
% initial feasible route
route = [starting_city, intermediate_cities, starting_city];
%display(route);
previous_distance = calculate_distance(route,distance_matrix);
%display(previous_distance);
for i = 1:m-2
    j = i + 1;
    while(j < m)
        %display(i)
        %display(j)
        a = intermediate_cities(1:i - 1);
        b = [intermediate_cities(j),intermediate_cities(i), intermediate_cities(i+1:j-1)];
        c = fliplr(intermediate_cities(j + 1:m - 1));
        new_route = [starting_city, a, b, c, starting_city];
        new_distance = calculate_distance(new_route, distance_matrix);
        if (new_distance < previous_distance)
            %display('new cost is lower');
            route = new_route;
            previous_distance = new_distance;
            %display(previous_distance)
            j = i + 1;
            continue;              
        else
           j = j + 1;
        end
   end        
end
cost = previous_distance;
end

function [dist] = calculate_distance(route, distance_matrix)
% calculating the cost of the route using the 
% distance matrix
dist = 0;
for i = 1: length(route) - 1 
    j = route(i);
    k = route(i + 1);
    dist = dist + distance_matrix(j,k);
end
end
