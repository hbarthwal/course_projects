'''
Created on Nov 10, 2013

@author: Himanshu Barthwal
'''
from pprint import pprint
from operator import itemgetter
from copy import deepcopy

class VariableElimination:

    def __init__(self, graph_matrix, nodes_to_be_eliminated):
        self._graph = graph_matrix
        self._nodes_to_be_eliminated = nodes_to_be_eliminated
        self._num_nodes = len(self._graph)
        self._induced_width = 0
        self._initialize_induced_graph()
        self._elimination_ordering = []


    def _initialize_induced_graph(self):
        '''
        Moralizes the given directed graph to get
        an undirected induced graph.
        '''
        self._induced_graph = deepcopy(self._graph)
        for i in range(self._num_nodes):
            for j in range(self._num_nodes):
                if i != j:
                    #  Copy edges from the original graph
                    #  to the undirected graph
                    if self._graph[i][j] == 1:
                        self._induced_graph[i][j] = 1
                        self._induced_graph[j][i] = 1

                    common_children = self._common_children(i, j)
                    if len(common_children) > 0:
                        #  Moralize all the v structures
                        self._induced_graph[i][j] = 1
                        self._induced_graph[j][i] = 1
                        self._induced_width = len(common_children) + 1

        print 'Induced Graph :-'
        pprint(self._induced_graph)

    def _common_children(self, i, j):
        '''
        Return True if node i and j have a common child, False otherwise.
        '''
        children_i = set([index for index, node in enumerate(self._graph[i]) if node == 1])
        children_j = set([index for index, node in enumerate(self._graph[j]) if node == 1])
        return children_i.intersection(children_j)

    def _get_cost(self, node):
        '''
        Calculates the cost of a node using the number of fill edges.
        '''
        fill_edge_count = 0
        neighbors = list([index for index, neighbor in enumerate(self._induced_graph[node]) if neighbor == 1])
        for i in neighbors:
            for j in neighbors:
                if i != j:
                #  If there is no edge between neighbors
                #  i and j then increment the fill_edge count
                    if self._induced_graph[i][j] == 0:
                        fill_edge_count += 1
        return fill_edge_count / 2

    def _get_min_cost_unmarked_node(self, nodes_status):
        '''
        Calculates the cost of each unmarked node
        and then returns the node with the minimum cost.
        '''
        #  Initialize cost dictionary
        cost_dict = {}
        #  Calculate the cost for all nodes
        for node in nodes_status:
            #  We only bother to calculate the cost of the
            #  unmarked nodes
            if nodes_status[node] == 'M':
                continue
            cost = self._get_cost(node)
            #  Add the cost to the dictionary
            cost_dict[node] = cost

        #  self.print_in_readable_form(cost_dict)

        cost_dict = sorted(cost_dict.items(), key = itemgetter(1))

        if len(cost_dict) == 0:
            return -1
        #  Return the node with minimum cost
        return cost_dict[0][0]

    def _update_induced_graph(self, eliminated_node):
        '''
        Updates the induced graph and returns the induced width
        of the induced subgraph.
        '''
        neighbors = list([index for index, neighbor
            in enumerate(self._induced_graph[eliminated_node]) if neighbor == 1])
        for i in neighbors:
            #  deleting the edges from eliminated node
            self._induced_graph[eliminated_node][i] = 0
            self._induced_graph[i][eliminated_node] = 0
            for j in neighbors:
                if i != j:
                    self._induced_graph[i][j] = 1

    def _greedy_ordering(self):
        #  Initializing all nodes as unmarked
        nodes_status = {}
        for node in self._nodes_to_be_eliminated:
            nodes_status[node] = 'U'

        while True:
            node = self._get_min_cost_unmarked_node(nodes_status)
            #  print 'Eliminating :', str(chr(ord('A') + node))
            if node == -1:
                break
            #  Set the node as marked.
            nodes_status[node] = 'M'
            #  Update the elimination ordering.
            self._elimination_ordering.append(node)
            self._update_induced_graph(node)

    def perform_variable_elimination(self):
        '''
        Returns the elimination ordering, induced graph matrix
        and the induced width.
        '''
        self._greedy_ordering()
        return self._elimination_ordering, self._induced_graph, self._induced_width

    def print_in_readable_form(self, dic):
        new_dict = {}
        for node in dic:
            new_dict[chr(ord('A') + node)] = dic[node]
        print new_dict

def main():
    print 'Problem 3(b)'
    graph = [
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
             ]

    nodes_to_be_eliminated = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
    ve = VariableElimination(graph, nodes_to_be_eliminated)
    order, graph, width = ve.perform_variable_elimination()

    print 'Elimination Order :-'
    order = [chr(ord('A') + node) for node in order]
    pprint(order)
    print 'Induced Width: ' , width

    print '------------------------------'
    print 'Problem 3(c)'
    graph = [
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             ]

    nodes_to_be_eliminated = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    ve = VariableElimination(graph, nodes_to_be_eliminated)
    order, graph, width = ve.perform_variable_elimination()

    print 'Elimination Order :-'
    order = [chr(ord('A') + node) for node in order]
    print order
    print 'Induced Width: ' , width

if __name__ == '__main__':
    main()



