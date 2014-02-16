'''
Created on Dec 9, 2013

@author: Himanshu Barthwal
'''
from collections import OrderedDict
from utils import BDeuScoreUtil, GraphUtils
from data_extractor import DataExtractor
from random_bn_generator import RandomBNGenerator
from networkx import draw
import matplotlib.pyplot as plt
from copy import deepcopy

class GreedyHillClimber:
    _max_change_count = 20

    def __init__(self, hyperparameter, initial_bayesian_network, tabu_list_size, max_change_count):
        self._bayesian_network = initial_bayesian_network
        self._best_score = -float('inf')
        self._best_solution = initial_bayesian_network
        self._actions_list = ['add', 'remove', 'reverse']
        self._tabu_list = OrderedDict()
        self._tabulist_size = tabu_list_size
        self._max_change_count = max_change_count
        self._data = DataExtractor(initial_bayesian_network.name)
        self._node_names = self._data.get_variable_values_sets().keys()
        values_sets = self._data.get_variable_values_sets()
        data_vectors = self._data.get_data_vectors()
        self._score_util = BDeuScoreUtil(hyperparameter, self._bayesian_network, data_vectors, values_sets)

    def _get_score(self, action = None, edge = None):
        #  We calculate the score using the BDeu score
        #  calculator
        return self._score_util.get_score(action, edge)

    def _equals(self, bayesian_network_A, bayesian_network_B):
        #  Return true if two bayesian network with identical nodes
        #  also have identical edges.
        signature_A = self._get_bn_signature(bayesian_network_A)
        signature_B = self._get_bn_signature(bayesian_network_B)
        return signature_A == signature_B

    def _tabu_list_contains(self, bayesian_network):
        #  Returns true if the tabu list contains the given
        #  bayesian network
        solution_signature = self._get_bn_signature(bayesian_network)
        has_solution = solution_signature in self._tabu_list
        if has_solution:
            pass    #  print 'solution is  contained in  tabulist(length = ', len(self._tabu_list), ')'
        else:
            pass    #  print  'solution is  not contained in  tabulist'
        return has_solution

    def _get_bn_signature(self, bayesian_network):
        #  Generate a string from the edge set of the given bayesian
        #  network which is unique for a given edge set
        edge_string_list = []
        for edge in bayesian_network.edges():
            edge_string = str(edge[0]) + '-' + str(edge[1])
            edge_string_list.append(edge_string)
        signature = ' '.join(edge_string_list)
        return signature

    def _add_solution_to_tabu_list(self, bayesian_network):
        #  Adds the given bayesian network to the tabu list
        if len(self._tabu_list) == self._tabulist_size:
            first_key = self._tabu_list.keys()[0]
            self._tabu_list.pop(first_key)

        solution_signature = self._get_bn_signature(bayesian_network)
        self._tabu_list[solution_signature] = 'dummy'

    def _get_feasible_local_solutions(self, bayesian_network, undirected_graph, edge):
        local_solutions_action_pairs = []
        #  Calculate all possible local solutions by applying
        #  all the possible actions.
        temp_bn = deepcopy(bayesian_network)
        temp_graph = deepcopy(undirected_graph)
        for action in self._actions_list:
            #  print action + 'ing', edge, ' in ', bayesian_network.edges()
            is_feasible = GraphUtils.apply_action(temp_bn, temp_graph, (edge), action, 2)

            if not is_feasible:
                #  If the action was not feasible  then try again
                #  print 'Infeasible action.. trying with different action'
                continue

            if self._tabu_list_contains(temp_bn):
                #  If generated solution is already in the tabu list then try again
                #  print 'Solution already in tabu list trying again'
                continue
            #  print 'Got ', temp_bn.edges()
            local_solutions_action_pairs.append((temp_bn, action))
            temp_bn = deepcopy(bayesian_network)
            temp_graph = deepcopy(undirected_graph)
        return local_solutions_action_pairs

    def _get_best_local_solution(self, bayesian_network, undirected_graph, edge):
        local_solutions_action_pairs = self._get_feasible_local_solutions(bayesian_network, undirected_graph, edge)
        if len(local_solutions_action_pairs) == 0:
            return self._get_score(bayesian_network), bayesian_network
        scores = [self._get_score(solution_action_pair[1], edge) for solution_action_pair in local_solutions_action_pairs]
        #  The solution with maximum score is the most optimal one
        sorted_scores = sorted(scores, reverse = True)
        #  print 'Scores: ', scores
        best_local_solution_score = sorted_scores[0]
        best_solution_index = scores.index(best_local_solution_score)
        #  print local_solutions_action_pairs[best_solution_index][1], ' action is the best action'
        best_local_solution = local_solutions_action_pairs[best_solution_index][0]
        return best_local_solution_score, best_local_solution

    def perform_GHC(self):
        current_solution = self._bayesian_network
        self._best_score = current_score = self._get_score(current_solution)
        #  draw(self._bayesian_network)
        #  plt.show()
        print 'Initial score :', self._best_score
        undirected_graph = current_solution.to_undirected()
        change_count = 0
        max_count = self._max_change_count
        print max_count
        while True:
            #  Pick a random edge and decide the best action to be
            #  applied on the edge
            random_edge = GraphUtils.get_random_edge(self._node_names)
            #  print random_edge, ' is the edge selected'
            current_score, current_solution = \
            self._get_best_local_solution(current_solution,
                                              undirected_graph, random_edge)
            undirected_graph = current_solution.to_undirected()

            if current_score > self._best_score:
                change_count = 0
                #  Update the new best solution
                self._best_solution = deepcopy(current_solution)
                self._best_score = current_score
                print '-----------', self._best_score , '------------------'

            else:
                change_count += 1

            self._add_solution_to_tabu_list(current_solution)

            if change_count == max_count:
                break

    def get_solution(self):
        return self._best_solution, self._best_score
