'''
Created on Nov 10, 2013

@author: Himanshu Barthwal
'''
from math import gamma, log, floor
from networkx import simple_cycles, is_connected, Graph, DiGraph
import itertools
from random import uniform
from os.path import join
import settings, sys
from itertools import product

class PGMUtils:

    @staticmethod
    def get_z_indices(Z, Z_combination, data_vectors):
        match_indices = []
        #  finding matches for the evidence variables 'Z'
        for index in range(len(Z_combination)):
            value_list = data_vectors[Z[index]]    #  The index of the value_list will give the
            #  index of data vector
            index_set = set()
            for element_index, element in enumerate(value_list):
                if element == Z_combination[index]:
                    index_set.add(element_index)

            match_indices.append(index_set)

        z_indices = match_indices[0]
        for indices in match_indices:
            #  The number of data vectors matching the given value
            #  combination of observed variables
            z_indices = z_indices.intersection(indices)
        return z_indices

    @staticmethod
    def get_combinations(variables, values_dict):
        if variables == None or len(variables) == 0:
            return []
        for variable in variables:
            value_lists = []
            for values in  values_dict[variable]:
                #  Gather all such lists in value_lists
                value_lists.append(values)
            value_combinations = list(product(value_lists))
            return value_combinations

class FileUtils:

    @staticmethod
    def get_network_filename(network_name):
        return join(settings.network_data_directory, network_name + '.json')
    @staticmethod
    def get_observed_data_filename(network_name):
        return join(settings.observed_data_directory, network_name + '.txt')

class GraphUtils:

    @staticmethod
    def is_degree_greater(graph, n):
        for node in graph.nodes():
            count = len(graph.neighbors(node))
            if count >= n:
                return True
        return False

    @staticmethod
    def convert_to_directed(graph):
        directed_graph = DiGraph()
        for edge in graph.edges():
            node1 = edge[0]
            node2 = edge[1]
            direction = graph[node1][node2]['direction']
            nodes = direction.split('->')
            src_node = nodes[0]
            dest_node = nodes[1]
            directed_graph.add_edge(*(src_node, dest_node))
        return directed_graph

    @staticmethod
    def rename_nodes(graph, node_names):
        new_graph = Graph()
        #  print len(self._node_names)
        for node in graph.nodes():
            #  Add all the nodes with the names given in the data set
            new_node_name = node_names[node]
            new_graph.add_node(new_node_name)

        for edge in graph.edges():
            #  Add all the  with the names given in the data set
            new_source_node = node_names[ edge[0] ]
            new_destination_node = node_names[ edge[1] ]
            new_graph.add_edge(new_source_node, new_destination_node)
        new_graph.name = graph.name
        return new_graph

    '''
    This class provides the miscellaneous functionalities which are
    used throughout the project.
    '''
    @staticmethod
    def _has_more_parents(bn, edge, max_parents):
        src_node = edge[0]
        dest_node = edge[1]
        src_node_parents_count = len(bn.predecessors(src_node))
        dest_node_parents_count = len(bn.predecessors(dest_node))
        if  src_node_parents_count > max_parents or dest_node_parents_count > max_parents:
            return False
        return True

    @staticmethod
    def _print_cause(has_cycle, has_more_parents, connected):
        if has_cycle:
            print 'Cycle found !'
        elif not connected:
            print 'Not connected !'
        elif has_more_parents:
            print 'More parents !!'

    @staticmethod
    def apply_action(bayesian_network, undirected_graph, edge, action, max_parents):
        has_cycle = has_more_parents = False
        connected = True
        #  print 'BN Edges:', bayesian_network.edges()
        #  print edge, ':', action
        if action == 'add':
            if not bayesian_network.has_edge(*edge):
                bayesian_network.add_edge(*edge)
                undirected_graph.add_edge(*edge)
                has_more_parents = not GraphUtils._has_more_parents(bayesian_network, edge, max_parents)
                has_cycle = GraphUtils.has_cycle(bayesian_network)
                #  GraphUtils._print_cause(has_cycle, _has_more_parents, connected)
                if (has_more_parents or has_cycle):
                    #  If cycle found or max parent constraint is violated,  revert back the add action
                    bayesian_network.remove_edge(*edge)
                    undirected_graph.remove_edge(*edge)
                    return False
            else:
                #  print 'Edge already in the graph !'
                return False

        elif action == 'remove':
            if bayesian_network.has_edge(*edge):
                bayesian_network.remove_edge(*edge)
                if undirected_graph.has_edge(*edge):
                    undirected_graph.remove_edge(*edge)
                #  check if the graph is still connected
                has_more_parents = not GraphUtils._has_more_parents(bayesian_network, edge, max_parents)
                connected = is_connected(undirected_graph)
                #  GraphUtils._print_cause(has_cycle, _has_more_parents, connected)
                if (has_more_parents or  not connected):
                    #  If not, then revert the changes
                    bayesian_network.add_edge(*edge)
                    undirected_graph.add_edge(*edge)
                    return False
            else:
                #  print 'No edge found to remove !'
                return False

        elif action == 'reverse':
            if bayesian_network.has_edge(*edge):
                reversed_edge = (edge[1], edge[0])
                bayesian_network.remove_edge(*edge)
                bayesian_network.add_edge(*reversed_edge)
                #  We don't need to update the undirected
                #  graph here
                has_more_parents = not GraphUtils._has_more_parents(bayesian_network, edge, max_parents)
                has_cycle = GraphUtils.has_cycle(bayesian_network)
                #  GraphUtils._print_cause(has_cycle, _has_more_parents, connected)

                if (has_more_parents or has_cycle):
                    #  Revert the changes
                    bayesian_network.remove_edge(*reversed_edge)
                    bayesian_network.add_edge(*edge)
                    return False
            else:
                #  print 'No edge found to reverse !'
                return False
        return True

    @staticmethod
    def get_random_edge(node_names):
        '''
        Generates a random edge from the provided node set.
        '''
        i = j = 0
        num_nodes = len(node_names)
        while i == j:
            i = int(floor(uniform(0, num_nodes)))
            j = int(floor(uniform(0, num_nodes)))
        i = node_names[i]
        j = node_names[j]
        return (i, j)

    @staticmethod
    def has_cycle(directed_graph):
        '''
        Return true if the directed_graph has cycles
        False, otherwise
        '''
        cycles = simple_cycles(directed_graph)
        if cycles == None :
            return True

        for cycle in cycles:
            if len(cycle) > 1:
                return True
        return False



    @staticmethod
    def test():
        from networkx import DiGraph
        bayesian_network = DiGraph()
        nodes = ["Pollution", "Smoker", "Cancer", "Xray", "Dyspnoea"]
        edges1 = [(u'Smoker', u'Xray'), (u'Cancer', u'Xray'), (u'Pollution', u'Dyspnoea'), (u'Pollution', u'Smoker')]
        edges2 = [["Pollution", "Cancer" ], ["Smoker", "Cancer"], ["Cancer", "Xray" ], [ "Cancer", "Dyspnoea" ]]
        print GraphUtils.get_hamming_distance(edges1, edges2)


        bayesian_network.add_nodes_from(["Pollution", "Smoker", "Cancer", "Xray", "Dyspnoea"])
        bayesian_network.add_edges_from(edges2)
        undirected_graph = bayesian_network.to_undirected()

        max_parents = 1
        edge = ["Smoker", "Cancer"]
        action = 'remove'
        is_feasible = GraphUtils.apply_action(bayesian_network, undirected_graph, edge, action, max_parents)
        print 'Feasible status:', is_feasible

        action = 'add'
        is_feasible = GraphUtils.apply_action(bayesian_network, undirected_graph, edge, action, max_parents)
        print 'Feasible status:', is_feasible

        action = 'reverse'
        is_feasible = GraphUtils.apply_action(bayesian_network, undirected_graph, edge, action, max_parents)
        print 'Feasible status:', is_feasible

class BDeuScoreUtil:
    '''
    This class provides the  functionality of calculating the BDeu 
    score for a given Bayesian Network.
    '''
    def __init__(self, hyperparameter, initial_bayesian_network, data_vectors, values_lists):
        self._parent_lists = {}
        self._score_dict = {}
        self._parent_configurations = {}
        self._bayesian_network = initial_bayesian_network
        self._undirected_graph = initial_bayesian_network.to_undirected()
        self._values_lists = values_lists
        self._data_vectors = data_vectors
        self._alpha = hyperparameter
        self._data_vectors_count = len(self._data_vectors[self._data_vectors.keys()[0]])
        #  print 'Data vector keys:', self._data_vectors.keys(), '--', len(self._data_vectors.keys())
        self._initialize_parent_list()
        self._initialize_parent_configurations()

    def get_score_dict(self):
        return self._score_dict

    def get_score(self, action = None, edge = None):
        '''
        Gets the score of the bayesian network subject to the change
        denoted by the (edge, action) pair. It only updates the underlying
        network temporarily and thus the changes are not reflected in the
        bayesian network to which this instance of BDeuScoreUtil is attached.
        Thus any changes should be done in the bayesian network whose reference was 
        provided while instantiation of the BDeuScoreUtil object.
        
        @param action: Can have 'add', 'remove' and 'reverse' values.
        @param edge: An edge on which action has to be applied
        '''
        variables = self._parent_lists.keys()
        if edge != None:
            #  print 'Calculating score for the network with edges :', self._bayesian_network.edges()
            #  print edge, action, ' is the applied change'
        #  If the score has been requested subject to a change
        #  (denoted by (edge, action) pair) in the  underlying
        #  bayesian network then we first have to update the network.
            variables = [edge[0], edge[1]]
            self._update_network(action, edge)
            #  print 'Calculating score for the network with edges(changed) :', self._bayesian_network.edges()
            self._populate_scores_dict(variables)

        else:
            #  We dont need to update the network.
            if not len(self._score_dict) :
                #  if the score dictionary is not populated
                #  then we populate it.
                self._populate_scores_dict(variables)

        #  calculate the score
        score = 0
        for V_i in self._score_dict:
            score += self._score_dict[V_i]
        self._revert_network(action, edge)
        #  print ' network edges after reverting:', self._bayesian_network.edges()
        return score

    def _initialize_parent_list(self):
        self._update_parent_list(self._bayesian_network.nodes())

    def _update_parent_list(self, nodes):
        #  Fetch the parent of each node in the nodes list
        #  and populate the parents list into the parent_lists dictionary.
        for node in nodes:
            parent_list = self._bayesian_network.predecessors(node)
            self._parent_lists[node] = sorted(parent_list)

    def _update_parent_configurations(self, children):
        for child in children:
            parents_value_lists = []
            for parent in self._parent_lists[child]:
                #  Fetch the possible values of the parent variable
                parent_value_list = self._values_lists[parent]

                #  Gather all such lists in parents_value_lists
                parents_value_lists.append(parent_value_list)

            #  The order of values in the final Cartesian
            #  product will be according to the alphabetic
            #  order of the parent variable names.
            combinations_parent_values = list(itertools.product(*parents_value_lists))
            self._parent_configurations[child] = combinations_parent_values

    def _initialize_parent_configurations(self):
        all_children = self._parent_lists.keys()
        self._update_parent_configurations(all_children)

    def _get_N_i_j_k(self, i, j, k):
            config = j
            variable_value = k
            #  We try to find out the data vector index which
            #  has the exact configuration of the parents present
            #  in it.
            match_indices = []

            parent_list = self._parent_lists[i]
            value_list = self._data_vectors[i]
            #  Now we look for the kth value of the variable i
            match_indices.append(set([element_index for element_index, element in enumerate(value_list) \
                                      if element == variable_value]))

            #  Here we exploit the fact that the config
            #  tuple is sorted in the order of the
            #  parents in the parents list.

            for index in range(len(config)):
                parent_key = parent_list[index]
                value_list = self._data_vectors[parent_key]
                #  The index of the value_list will give the
                #  index of data vector
                index_set = set()
                for element_index, element in enumerate (value_list) :
                    if element == config[index]:
                        index_set.add(element_index)
                match_indices.append(index_set)

            #  If we could not find the combination in any data vector
            #  we say the value of N_i_j_k to equal to zero.
            if not len(config) + 1 == len(match_indices):
                return 0

            #  The number of data vectors matching the given parent configurations
            #  and the value of the variable under consideration is given
            #  by the number of elements in the intersection of the sets in the
            #  match indices list.
            intersecting_indices = match_indices[0]
            for indices in match_indices:
                intersecting_indices = intersecting_indices.intersection(indices)

            #  We normalize it in order to avoid very high values
            N_i_j_k = len(intersecting_indices)
            #  print N_i_j_k

            return N_i_j_k / float(len(self._data_vectors))

    def _get_term_one(self, V_i, j, q_i, sum_N_i_j_k):
        x = self._alpha / float(q_i)
        y = sum_N_i_j_k
        term = log(gamma(x)) - log(gamma(x + y))
        return term

    def _get_term_two(self, q_i, r_i, N_i_j_k):
        x = self._alpha / float(q_i * r_i)
        y = x + N_i_j_k
        term = log(gamma(y)) - log(gamma(x))
        return term

    def _revert_network(self, action, edge):
        #  Reverses the actions which were applied on the
        #  given edge
        if edge == None:
            return
        if action == 'add':
            action = 'remove'
        elif action == 'remove':
            action = 'add'

        self._update_network(action, edge)

    def _update_network(self, action, edge):
        is_feasible = GraphUtils.apply_action(self._bayesian_network, self._undirected_graph, edge, action, sys.maxint)
        if not is_feasible:
            #  Dont change the network and just return as if nothing happened
            return
        else:
            variables = [edge[0], edge[1]]
            self._update_parent_list(variables)
            self._update_parent_configurations(variables)

    def _populate_scores_dict(self, variables):
        '''
        Calculates the score for each variable in the bayesian network
        and populates the score dictionary.  
        '''
        for V_i in variables:
            term_two = 0
            term_one = 0
            #  Here 'V_i' represents the current node whose Bdeu score
            #  is to be calculated

            #  r_i is the number of values that can be taken by i
            r_i = len(self._values_lists[V_i])

            #  q_i is the number of configurations that are possible
            #  for the parents of V_i
            q_i = len(self._parent_configurations[V_i])

            for j in self._parent_configurations[V_i]:
                #  j is the enumeration over the possible
                #  configurations of the parents of V_i
                sum_N_i_j_k = 0
                for k in self._values_lists[V_i]:
                    #  k is the enumeration over the possible
                    #  values of V_i
                    N_i_j_k = self._get_N_i_j_k(V_i, j, k)
                    term_two += self._get_term_two(q_i, r_i, N_i_j_k)
                    #  We use this to calculate  term one
                    #  in the BDeu formula
                    sum_N_i_j_k += N_i_j_k

                term_one += self._get_term_one(V_i, j, q_i, sum_N_i_j_k)

            #  We keep scores for all the variables separately because
            #  its quicker to partially update the score if there is
            #  minor change in the corresponding bayesian network

            self._score_dict[V_i] = term_one + term_two

    @staticmethod
    def test():
        from data_extractor import DataExtractor
        from networkx import DiGraph

        network_name = 'cancer'
        #  getting data for the bayesian network
        data = DataExtractor(network_name)
        data_vectors = data.get_data_vectors()
        value_sets = data.get_variable_values_sets()

        bayesian_network1 = DiGraph()
        bayesian_network1.add_nodes_from(["Pollution", "Smoker", "Cancer", "Xray", "Dyspnoea"])

        bayesian_network2 = DiGraph()
        bayesian_network2.add_nodes_from(["Pollution", "Smoker", "Cancer", "Xray", "Dyspnoea"])
        bayesian_network2.add_edges_from([["Pollution", "Cancer" ], ["Smoker", "Cancer"], ["Cancer", "Xray" ], [ "Cancer", "Dyspnoea" ]])

        score_util = BDeuScoreUtil(1 , bayesian_network1, data_vectors, value_sets)
        score = score_util.get_score()
        print 'Network before:', bayesian_network1.edges(), 'Score : ', score
        score = score_util.get_score('add', ["Pollution", "Cancer"])

        print 'Network after::', bayesian_network1.edges(), 'Score : ', score
        print 'BN1:'
        print score_util.get_score_dict()
        print score

        score_util = BDeuScoreUtil(1, bayesian_network2, data_vectors, value_sets)
        score = score_util.get_score()
        print 'BN2:'

        print score_util.get_score_dict()
        print score

def main():
    BDeuScoreUtil.test()
    GraphUtils.test()

if __name__ == '__main__':
    main()
