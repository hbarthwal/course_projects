'''
Created on Dec 10, 2013

@author: himanshu
'''
from data_extractor import DataExtractor
from utils import PGMUtils

class ParameterEstimation:
    def __init__(self, network):
        self._network = network
        self._data = DataExtractor(network.name)

    def _get_probabilities(self, X, S, S_combinations):
        data_vectors = self._data.get_data_vectors()
        N = len(data_vectors[data_vectors.keys()[0]])
        X_values = data_vectors[X]
        observed_prob_dict = {}
        #  Now we look for the  value x of the variable X
        for x in self._values_dict[X]:
            #  finding matches for x
            x_indices = set([element_index for (element_index, element) in enumerate(X_values) if element == x])
            observed_prob_dict['P(' + X + '=' + x + ')'] = (len(x_indices) / N) + 0.001

            for S_combination in S_combinations:
                z_indices = self._get_z_indices(S, S_combination)
                z = z_indices
                x_z = x_indices.intersection(z)
                observed_prob_dict['P(' + X + '=' + x + '|' + ','.join(S) + '=' + ','.join(S_combination) + ')'] = (len(x_z) / float(len(z))) + 0.001
        return observed_prob_dict

    def get_estimated_cpds(self):
        values_dict = self._data.get_variable_values_sets()
        cpds = []
        for node in self._network:
            parents = self._network.predecessors(node)
            value_combinations = PGMUtils.get_combinations(parents, values_dict)
            probability_dict = self._get_probabilities(node, parents, value_combinations)
            cpds.append(probability_dict)
        return cpds














