'''
Created on Dec 8, 2013

@author: himanshu
'''

from networkx import Graph, complete_graph, all_simple_paths, draw, is_connected
from data_extractor import DataExtractor
from itertools import combinations, product
from math import log
from utils import GraphUtils, PGMUtils
from operator import itemgetter
import matplotlib.pyplot as plt
from pprint import pprint
import settings

class PC:

    _mutual_info_thresholds = [0.0005, 0.005, 0.025, 0.025]

    def __init__(self, network_name):
        self._network_name = network_name
        self._data = DataExtractor(network_name)
        self._values_dict = self._data.get_variable_values_sets()
        self._node_names = self._values_dict.keys()
        self._graph = None
        self._nmis = {}

    def _get_probabilities(self, X, Y, S, S_combinations):
        data_vectors = self._data.get_data_vectors()
        N = len(data_vectors[data_vectors.keys()[0]])
        X_values = data_vectors[X]
        Y_values = data_vectors[Y]
        observed_prob_dict = {}
        #  Now we look for the  value x of the variable X, and value y of the variable Y
        for x in self._values_dict[X]:    #  finding matches for x
            x_indices = set([element_index for (element_index, element) in enumerate(X_values) if element == x])
            observed_prob_dict['P(' + X + '=' + x + ')'] = len(x_indices) / float(N)
            for y in self._values_dict[Y]:
                #  finding matches for y
                y_indices = set([element_index for (element_index, element) in enumerate(Y_values) if element == y])
                observed_prob_dict['P(' + Y + '=' + y + ')'] = len(y_indices) / float(N)
                xy = x_indices.intersection(y_indices)
                observed_prob_dict['P(' + X + '=' + x + ',' + Y + '=' + y + ')'] = len(xy) / float(N)

                for S_combination in S_combinations:
                    z_indices = PGMUtils.get_z_indices(S, S_combination, data_vectors)
                    z = z_indices
                    y_z = y_indices.intersection(z)
                    x_z = x_indices.intersection(z)
                    xyz = xy.intersection(z)
                    observed_prob_dict['P(' + X + '=' + x + '|' + ','.join(S) + '=' + ','.join(S_combination) + ')'] = len(x_z) / float(len(z))
                    observed_prob_dict['P(' + ','.join(S) + '=' + ','.join(S_combination) + ')'] = len(z) / float(N)
                    observed_prob_dict['P(' + Y + '=' + y + '|' + ','.join(S) + '=' + ','.join(S_combination) + ')'] = len(y_z) / float(len(z))
                    observed_prob_dict['P(' + X + '=' + x + ',' + Y + '=' + y + ',' + ','.join(S) + '=' + ','.join(S_combination) + ')'] = len(xyz) / float(N)
        return observed_prob_dict

    def _are_dseparated(self, X, Y, S, n):
        H_X = H_Y = H_XY = 0
        S_combinations = PGMUtils.get_combinations(S, self._values_dict)
        probability_dict = self._get_probabilities(X, Y, S, S_combinations)
        for x in self._values_dict[X]:
            p_x = probability_dict['P(' + X + '=' + x + ')']
            for y in self._values_dict[Y]:
                p_y = probability_dict['P(' + Y + '=' + y + ')']
                #  in case we are looking for zero order conditional dependency
                if len(S_combinations) == 0:
                    H_Y += -log(p_y + 0.001)
                    H_X += -log(p_x + 0.001)
                    p_xy = probability_dict['P(' + X + '=' + x + ',' + Y + '=' + y + ')']
                    H_XY += -log(p_xy + 0.001)
                else:
                    for S_combination in S_combinations:
                        p_y_z = probability_dict['P(' + Y + '=' + y + '|' + ','.join(S) + '=' + ','.join(S_combination) + ')']
                        p_x_z = probability_dict['P(' + X + '=' + x + '|' + ','.join(S) + '=' + ','.join(S_combination) + ')']
                        p_xyz = probability_dict['P(' + X + '=' + x + ',' + Y + '=' + y + ',' + ','.join(S) + '=' + ','.join(S_combination) + ')']
                        p_z = probability_dict['P(' + ','.join(S) + '=' + ','.join(S_combination) + ')']
                        H_X += -log(p_x_z + 0.001)
                        H_Y += -log(p_y_z + 0.001)
                        H_XY += -log(p_xyz * p_z + 0.001)

        #  If mutual information is greater than certain threshhold
        #  then X and Y are dependent otherwise not
        n_X = 2 * len(self._values_dict[X])
        n_Y = 2 * len(self._values_dict[Y])
        n_XY = 4 * len(S_combinations)
        if n_XY == 0:
            n_XY = 4
        MI = abs((H_X / n_X) + (H_Y / n_Y) - (H_XY / n_XY))
        #  print 'MI(', X + ',' + Y + '|' + ','.join(S), ') = ', MI
        self._nmis[X + ',' + Y + '|' + ','.join(S)] = MI
        if MI < self._mutual_info_thresholds[n]:
            return True
        return False

    def _eliminate_edges(self, Sep):
        num_nodes = len(self._values_dict.keys())
        graph = complete_graph(num_nodes, Graph())
        self._graph = GraphUtils.rename_nodes(graph, self._node_names)
        n = 0
        max_allowed_degree = settings.networks_settings['genome']['max_allowed_degree']
        while n <= 3:
            print '--------------------------------------------------------'
            #  We repeat the iterations unless each node X has
            #  less than or equal to n neighbors
            for X in self._graph:
                for Y in self._graph:
                    if X != Y and GraphUtils.is_degree_greater(self._graph, max_allowed_degree) \
                    and is_connected(self._graph):
                        #  all the neighbors of X excluding Y
                        neighbors = self._graph.neighbors(X)
                        if Y in neighbors:
                            neighbors.remove(Y)
                            #  We only consider X,Y if #neighbors of X excluding Y are more than
                            #  or equal to n
                            if len(neighbors) >= n:
                                #  Combinations of all the adjacent nodes of X excluding Y
                                #  each subset in the observed_sets has cardinality 'n'
                                observed_subsets = combinations(neighbors, n)
                                for S in observed_subsets:
                                    #  We only consider the subsets which have exactly
                                    S = [s for s in sorted(S)]
                                    are_deseparated = self._are_dseparated(X, Y, S, n)
                                    if are_deseparated:
                                        if self._graph.has_edge(X, Y):
                                            self._graph.remove_edge(X, Y)
                                            print 'Removed', X, '-', Y
                                            Sep[X + ',' + Y] = S
                                            Sep[Y + ',' + X] = S
            n += 1

    def _has_directed_path(self, A, B):
        has_directed_path = False
        paths = all_simple_paths(self._graph, A, B)
        for path in paths:
            has_directed_path = has_directed_path or has_directed_path
            if has_directed_path:
                break
            i = 0
            while i < len(path) - 1:
                src_node = path[i]
                next_node = path[i + 1]
                edge = self._graph.edge[src_node] [next_node]
                if 'direction' in edge:
                    if edge['direction'] == src_node + '->' + next_node:
                        has_directed_path = True
                else:
                    has_directed_path = False
                    break
                i += 1
        return has_directed_path

    def _all_edges_oriented(self):
        '''
        for edge in self._graph.edges():
            if 'direction'in self._graph[edge[0]][edge[1]]:
                print self._graph[edge[0]][edge[1]]['direction']
        '''
        for edge in self._graph.edges():
            if 'direction'not in self._graph[edge[0]][edge[1]]:
                return False
        return True

    def _orient_edges(self, Sep):
        triplets = []
        for source in self._graph.nodes():
            for target in self._graph.nodes():
                if source != target:
                    if not self._graph.has_edge(source, target):
                        #  Each element in triplets lists will be a list of three nodes
                        #  [X, Y , Z] such that X and Z are not adjacent in the graph
                        #  while X,Y and Y,Z are adjacent
                        triplets.append(list(all_simple_paths(self._graph, source, target, 2)))

        for triplet in triplets:
            if triplet != []:
                X, Y , Z = triplet[0][0], triplet[0][1], triplet[0][2]
                if Y not in Sep[X + ',' + Z]:
                    #  We dont have partially connected graphs in networkx library
                    #  so we attach a direction attribute to all the edges which we
                    #  want to be directed
                    edgeXY = self._graph.edge[X][Y]
                    edgeXY['direction'] = X + '->' + Y
                    edgeZY = self._graph.edge[Z][Y]
                    edgeZY['direction'] = Z + '->' + Y

        while not self._all_edges_oriented():
            for edge in self._graph.edges():
                A = edge[0]
                B = edge[1]
                edgeAB = self._graph.edge[A][B]
                if 'direction' in edgeAB:
                    if edgeAB['direction'] == A + '->' + 'B':
                        for C in self._graph.neighbors(B):
                            #  A & C are not adjacent
                            if not self._graph.has_edge(A, C):
                                edgeBC = self._graph.edge[B][C]
                                if 'direction' not in edgeBC:
                                    edgeBC['direction'] = B + '->' + C

                elif self._has_directed_path(A, B):
                    edgeAB['direction'] = A + '->' + B

    def perform_PC(self):
        #  Implementation of the PC algorithm given here:
        #  http://www.lowcaliber.org/influence/spirtes-causation-prediction-search.pdf
        Sep = {}
        self._eliminate_edges(Sep)
        pprint(sorted(self._nmis.iteritems(), key = itemgetter(1), reverse = True))
        print self._graph.edges()
        draw(self._graph)
        plt.show()
        if is_connected(self._graph):
            print 'The graph is connected'
        else:
            print 'The graph is not connected'

        self._orient_edges(Sep)
        pprint (self._graph.edges())

    def get_skeleton(self):
        self._graph = GraphUtils.convert_to_directed(self._graph)
        self._graph.name = self._network_name
        return self._graph

def main():
    pc = PC('genome')
    pc.perform_PC()
    bn = pc.get_skeleton()
    draw(bn)
    plt.show()

if __name__ == '__main__':
    main()
