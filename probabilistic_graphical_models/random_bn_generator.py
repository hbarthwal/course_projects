'''
Created on Nov 9, 2013

@author: Himanshu Barthwal
'''
import matplotlib.pyplot as plt
from networkx import DiGraph, draw, balanced_tree
from data_extractor import DataExtractor
from math import pow, log, floor
import settings
from utils import GraphUtils
from copy import deepcopy
class RandomBNGenerator:
    '''
    A randomized construction heuristic for generating initial bayesian network 
    with a given number of nodes.  
    '''
    def __init__(self, network_name, num_BNs, max_parents):
        self._num_BNs = num_BNs
        self._network_name = network_name
        self._data_extractor = DataExtractor(network_name)
        self._node_names = self._data_extractor.get_variable_values_sets().keys()
        self._num_nodes = len(self._data_extractor.get_variable_values_sets())
        self._max_parents = max_parents
        if num_BNs > pow(2, (self._num_nodes * (self._num_nodes - 1)) / float(2)):
            raise('Invalid number of unique bayesian networks!')

    def _generate_initial_graph(self):
        #  Generated a simple ordered tree
        height = floor(log(self._num_nodes) / log(2))
        graph = balanced_tree(2, height, DiGraph())
        for node in graph.nodes():
            if int(node) >= self._num_nodes:
                graph.remove_node(node)
        #  We rename the nodes according to the target bayesian
        #  network we are trying to learn
        return self._rename_nodes(graph)

    def get_bayesian_networks(self):
        bayesian_network = GraphUtils.read_graph(self._network_name + '-' + str(self._max_parents))
        bayesian_networks = []

        if bayesian_network == None:
            #  Generate a tree (graph) with required number of nodes.
            bayesian_network = self._generate_initial_graph()
            bayesian_network.name = self._network_name + '-' + str(self._max_parents)
            GraphUtils.write_graph(bayesian_network)
            #  theoretical bound is infinity but this also does well
        num_iterations = 4 * self._num_nodes * self._num_nodes

        #  Since connectedness is only defined for undirected graphs
        #  so we have to keep a copy of the bayesian network
        #  except that all the edges are undirected
        undirected_BN = bayesian_network.to_undirected()
        bayesian_network.name = self._network_name
        #  Repeat for a large number of times.
        for i in xrange(self._num_BNs):
            count, i, j = 0, 0, 0;
            while count < num_iterations:
                edge = (i, j) = GraphUtils.get_random_edge(self._node_names)

                if bayesian_network.has_edge(*edge):
                    #  If (i,j) is in the graph, remove it
                    GraphUtils.apply_action(bayesian_network, undirected_BN, edge, 'remove', self._max_parents)
                else:
                    #  If the edge  (i,j) is not in the graph, add it.
                    GraphUtils.apply_action(bayesian_network, undirected_BN, edge, 'add', self._max_parents)
                count += 1
            bayesian_networks.append(deepcopy(bayesian_network))

        #  Return the obtained graph
        return bayesian_networks

    def _rename_nodes(self, graph):
        new_graph = DiGraph()
        #  print len(self._node_names)
        for node in graph.nodes():
            #  Add all the nodes with the names given in the data set
            new_node_name = self._node_names[node]
            new_graph.add_node(new_node_name)

        for edge in graph.edges():
            #  Add all the  with the names given in the data set
            new_source_node = self._node_names[ edge[0] ]
            new_destination_node = self._node_names[ edge[1] ]
            new_graph.add_edge(new_source_node, new_destination_node)
        new_graph.name = self._network_name
        return new_graph

    def _exceeded_parent_limit(self, bayesian_network, node):
        return len(bayesian_network.predecessors(node)) > self._max_parents

    @staticmethod
    def test():
        generator = RandomBNGenerator('cancer', 3, max_parents = 2);
        bns = generator.get_bayesian_networks()
        for bn in bns:
            print bn.nodes()
            print GraphUtils.has_cycle(bn)
            draw(bn)
            plt.show()

def main():
    RandomBNGenerator.test()

if __name__ == '__main__':
    main()
