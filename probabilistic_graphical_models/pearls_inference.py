'''
Created on Dec 1, 2013

@author: himanshu
'''
from networkx import DiGraph
from itertools import product
from operator import mul, add
from string import split
from pprint import pprint

class Utils:
    @staticmethod
    def get_cpd_key(variable_name_value_pair, conditioned_variables_name_value_pairs):
        #  we represent the a varibale named A taking a value 0 as A(0)
        variable_key = variable_name_value_pair[0] + variable_name_value_pair[1]
        condtioned_variables_list = []
        for conditioned_variables_name_value_pair in conditioned_variables_name_value_pairs:
            conditioned_variable_key = conditioned_variables_name_value_pair[0] + conditioned_variables_name_value_pair[1]
            condtioned_variables_list.append(conditioned_variable_key)
        cpd_key = variable_key
        if len(condtioned_variables_list) > 0:
            cpd_key = cpd_key + '|' + ','.join(sorted(condtioned_variables_list))
        return cpd_key

    @staticmethod
    def get_variable_and_conditioned_variables(cpd_key):
        variables = cpd_key.split('|')
        variable = [variables[0][0], variables[0][1]]
        conditioned_variables = []
        if len(variables) > 1:
            conditioned_variables_values = variables[1].split(',')
            for conditioned_variables_value in conditioned_variables_values:
                conditioned_variables.append([conditioned_variables_value[0], conditioned_variables_value[1]])
        return variable, sorted(conditioned_variables)

    @staticmethod
    def test():
        v_pair = ['A', '1']
        cv_pairs = [('C', '0'), ['B', '1']]
        print Utils.get_cpd_key(v_pair, cv_pairs)

class PearlsInference:
    '''
    Implementation of the Pearl's message passing algorithm for 
    inference in poly-trees.
    '''
    def __init__(self, bayesian_network, conditional_probabilities):
        self._bayesian_network = bayesian_network
        self._root_nodes = []
        self._conditional_probabilities = conditional_probabilities
        #  This set just contains the set of variables that have been observed
        self._evidence_set = set()
        #  This dict contains the observed variable names as keys and
        #  the list of  observed  values as  the values
        self._evidence_values_dict = {}
        #  We initialize the network with the given conditional probabilities
        self._initialize_network()

    def _initialize_dictionaries(self):
        #  We initialize every dictionary here in order to avoid the
        #  checks for the presence of keys
        for node in self._bayesian_network.nodes():
            node_object = self._bayesian_network.node[node]
            if 'values' not in node_object:
                print node
                raise('No values were provided for the node')

            node_object['lambda_messages'] = {}
            node_object['lambda_values'] = {}
            node_object['pi_messages'] = {}
            node_object['pi_values'] = {}

    def _initialize_lambda_values(self, node):
        node_object = self._bayesian_network.node[node]
        #  The values keys has a list of all the values that this
        #  node can take.
        node_values = node_object['values']    #  This dictionary will contain the lambda values for all the
        #  node values each entry will be key : value pair
        #  with node value as the key and the corresponding
        #  lambda value as the value
        lambda_values = node_object['lambda_values'] = {}
        #  Now we initialize all the lambda values to 1.
        for value in node_values:
            lambda_values[value] = 1

    def _initialize_lambda_messages(self, node):
        node_object = self._bayesian_network.node[node]
        #  This dictionary holds the lambda messages sent by
        #  'node' to its parents. Each key is the name of parent
        #  and the value is  a dictionary. which has the lambda messages
        #  for all the values of the parent node.
        lambda_messages = node_object['lambda_messages'] = {}
        #  We loop over the parents of 'node'
        for parent in self._bayesian_network.predecessors(node):
            #  We initialize the lambda messages dictionary for this parent
            lambda_messages[parent] = {}
            #  We get the list of the possible values of the parent
            parent_values = self._bayesian_network.node[parent]['values']
            #  We loop over the parent values
            for parent_value in parent_values:
                #  Initialize the lambda message
                lambda_messages[parent][parent_value] = 1

    def _initialize_pi_messages(self, node):
        node_object = self._bayesian_network.node[node]
        #  This dictionary holds the pi messages sent by
        #  'node' to its children. Each key is the name of child
        #  and the value is  a dictionary. which has the pi messages
        #  for all the values of the child node.
        pi_messages = node_object['pi_messages'] = {}
        #  We loop over the children of 'node'
        for child in self._bayesian_network.successors(node):
            #  We initialize the pi messages dictionary for this child
            pi_messages[child] = {}
            #  We get the list of the possible values of the child
            node_values = node_object['values']
            #  We loop over the child values
            for node_value in node_values:
                #  Initialize the pi message
                pi_messages[child][node_value] = 1

    def _get_root_nodes(self):
        root_nodes = []
        for node in self._bayesian_network.nodes():
            if len(self._bayesian_network.predecessors(node)) == 0:
                #  All the nodes having no parents are root nodes
                root_nodes.append(node)
        return root_nodes

    def _initialize_pi_values_for_root_nodes(self):
        root_nodes = self._get_root_nodes()
        #  Loop over all the root nodes
        for root_node in root_nodes:
            #  loop over all the values that can be held by
            #  the root nodes
            root_node_object = self._bayesian_network.node[root_node]
            root_node_values = root_node_object['values']
            #  We initialize the pi values dictionary for this rot node
            pi_values = root_node_object['pi_values']

            for root_node_value in root_node_values:
                #  Note that the evidence set is empty here
                #  therefore effectively this conditional probability is  marginal probability
                #  of the root_node
                cpd_key = Utils.get_cpd_key((root_node, root_node_value), self._evidence_set)
                if cpd_key in self._conditional_probabilities:
                    #  Check if the probability was provided
                    pi_values[root_node_value] = self._conditional_probabilities[cpd_key]
                    #  Note that we do not need to update the conditional probability
                    #  because the evidence set is empty.
                else:
                    #  Raise error otherwise
                    raise('The marginal probability of a root node is missing')
            for child in self._bayesian_network.successors(root_node):
                #  Send a pi message to all the children of root nodes
                self._send_pi_message(root_node, child)

    def _initialize_network(self):
        self._initialize_dictionaries()
        for node in self._bayesian_network.nodes():
            self._initialize_lambda_values(node)
            self._initialize_lambda_messages(node)
            self._initialize_pi_messages(node)
        self._initialize_pi_values_for_root_nodes()

    def _update_pi_messages(self, parent, child):
        parent_node_object = self._bayesian_network.node[parent]
        parent_values = parent_node_object['values']
        parent_pi_values = parent_node_object['pi_values']
        pi_messages = parent_node_object['pi_messages'][child]
        for parent_value in parent_values:
            children = self._bayesian_network.successors(parent)
            children.remove(child)
            other_children = children
            child_lambda_messages_product = 1
            for other_child in other_children:
                other_child_node_object = self._bayesian_network.node[other_child]
                other_child_lambda_messages = other_child_node_object['lambda_messages']
                child_lambda_messages_product = child_lambda_messages_product \
                 * other_child_lambda_messages[parent][parent_value]
            pi_messages[parent_value] = parent_pi_values[parent_value] * child_lambda_messages_product

    def _compute_pi_value(self, node, node_value):
        parent_list = self._bayesian_network.predecessors(node)
        parent_values_combinations = self._get_parent_configurations(parent_list)


        #  Each element in 'products' list corresponds to the product of the
        #  conditional probability and the corresponding pi values
        #  for all the possible configurations of the child and parent
        #  values.
        products = []
        for combination in parent_values_combinations:
            pi_message_list = []
            conditioned_variables = []

            for i in xrange(len(parent_list)):
                parent = parent_list[i]
                parent_value = combination[i]
                conditioned_variables.append([parent, parent_value ])
                parent_node_object = self._bayesian_network.node[parent]
                pi_messages = parent_node_object['pi_messages']
                pi_message_list.append(pi_messages[node][parent_value])

            cpd_key = Utils.get_cpd_key([node, node_value], conditioned_variables)
            probability = self._conditional_probabilities[cpd_key]
            pi_messages_product = reduce(mul, pi_message_list)
            products.append(probability * pi_messages_product)

        sum_of_products = reduce(add, products)
        return sum_of_products

    def _send_pi_message(self, parent, child):
        print 'sending pi message from ', parent, ' ', child
        #  Update the pi messages
        self._update_pi_messages(parent, child)

        #  Update the pi values
        child_node_object = self._bayesian_network.node[child]
        child_pi_values = child_node_object['pi_values']
        child_lambda_values = child_node_object['lambda_values']
        child_values = child_node_object['values']
        psuedo_probability_dict = {}
        if child not in self._evidence_set:
            for child_value in child_values:
                child_pi_values[child_value] = self._compute_pi_value(child, child_value)
                psuedo_probability_dict[child_value] = child_pi_values[child_value] * child_lambda_values[child_value]

            #  Calculate the normalization factor
            alpha = reduce(add, psuedo_probability_dict.values())
            for child_value in child_values:
                cpd_key = Utils.get_cpd_key([child, child_value], self._evidence_values_dict.items())
                #  update the conditional probabilities
                self._conditional_probabilities[cpd_key] = psuedo_probability_dict[child_value] / alpha

            #  Sending pi messages to all the children of the 'child' node
            childs_children = self._bayesian_network.successors(child)
            for childs_child in childs_children:
                self._send_pi_message(child, childs_child)

        #  Sending message to the active parents of the 'child' node
        is_active = False
        for lambda_value in child_lambda_values.values() :
            if lambda_value != 1:
                is_active = True
                break
        if is_active:
            parents = self._bayesian_network.predecessors(child)
            parents.remove(parent)
            for parent in parents:
                if parent not in self._evidence_set:
                    self._send_lambda_message(child, parent)

    def _get_parent_configurations(self, parent_list):
        parents_value_lists = []
        for parent in parent_list:
            #  Fetch the possible values of the parent variable
            parent_node_object = self._bayesian_network.node[parent]
            parent_value_list = parent_node_object['values']

            #  Gather all such lists in parents_value_lists
            parents_value_lists.append(parent_value_list)

        #  The order of values in the final Cartesian
        #  product will be according to the alphabetic
        #  order of the parent variable names.
        combinations_parent_values = list(product(*parents_value_lists))
        return combinations_parent_values

    def _update_lambda_message(self, node, excluded_parent_name, excluded_parent_value):
        lambda_message = 0
        child_node_object = self._bayesian_network.node[node]
        child_values = child_node_object['values']
        child_lambda_values = child_node_object['lambda_values']
        child_lambda_messages = child_node_object['lambda_messages'][excluded_parent_name]
        parent_list = self._bayesian_network.predecessors(node)
        parent_list.remove(excluded_parent_name)
        parent_values_combinations = self._get_parent_configurations(parent_list)
        #  Each element in this list corresponds to the product of the
        #  conditional probability and the corresponding pi values
        #  for all the possible configurations of the child and parent
        #  values.
        for child_value in child_values:
            products = []
            pi_message_list = [1]
            for combination in parent_values_combinations:
                conditioned_variables = [[excluded_parent_name, excluded_parent_value]]
                for i in xrange(len(parent_list)):
                    parent = parent_list[i]
                    parent_value = combination[i]
                    conditioned_variables.append([parent, parent_value ])
                    parent_node_object = self._bayesian_network.node[parent]
                    pi_message = parent_node_object['pi_messages'][node][parent_value]
                    pi_message_list.append(pi_message)

                cpd_key = Utils.get_cpd_key([node, child_value], conditioned_variables)
                probability = self._conditional_probabilities[cpd_key]
                pi_messages_product = reduce(mul, pi_message_list)
                products.append(probability * pi_messages_product)

            sum_of_products = reduce(add, products)
            child_lambda_value = child_lambda_values[child_value]
            lambda_message = lambda_message + child_lambda_value * sum_of_products
        child_lambda_messages[excluded_parent_value] = lambda_message

    def _compute_lambda_value(self, node, value):
        lambda_message_product = 1
        for child in self._bayesian_network.successors(node):
            child_node_object = self._bayesian_network.node[child]
            lambda_messages = child_node_object['lambda_messages']
            lambda_message = lambda_messages[node][value]
            lambda_message_product = lambda_message_product * lambda_message
        return lambda_message_product

    def _send_lambda_message(self, child, parent):
        print 'sending lambda message from ', child, ' to ', parent
        parent_node_object = self._bayesian_network.node[parent]
        parent_values = parent_node_object['values']

        parent_lambda_values = parent_node_object['lambda_values']
        parent_pi_values = parent_node_object['pi_values']
        psuedo_probability_dict = {}
        for parent_value in parent_values:
            self._update_lambda_message(child, parent, parent_value)
            parent_lambda_values[parent_value] = self._compute_lambda_value(parent, parent_value)
            psuedo_probability_dict[parent_value] = parent_pi_values[parent_value] * parent_lambda_values[parent_value]

        #  Calculate the normalization factor
        alpha = reduce(add, psuedo_probability_dict.values())
        for parent_value in parent_values:
            cpd_key = Utils.get_cpd_key([parent, parent_value], self._evidence_values_dict.items())
            #  update the conditional probabilities
            self._conditional_probabilities[cpd_key] = psuedo_probability_dict[parent_value] / alpha

        #  Sending lambda messages to the parents of the 'parent'
        #  node
        for grand_parent in self._bayesian_network.predecessors(parent):
            if grand_parent not in self._evidence_set:
                self._send_lambda_message(parent, grand_parent)

        #  Sending pi messages to all the children of the 'parent' node
        #  excluding the 'child' node
        children = self._bayesian_network.successors(parent)
        children.remove(child)
        for child in children:
            self._send_pi_message(parent, child)

    def _update_evidence_node_data(self, observed_variable, observed_value):
        #  Update the evidence sets
        self._evidence_set = self._evidence_set.union(observed_variable)
        self._evidence_values_dict[observed_variable] = observed_value
        variable_node = self._bayesian_network.node[observed_variable]
        #  Fetch the different dictionaries corresponding to this node
        values = variable_node['values']
        lambda_values = variable_node['lambda_values']
        pi_values = variable_node['pi_values']
        assigned_value = None
        #  We update the pi values , lambda values and the
        #  conditional probabilities according to the new evidence
        for value in values:
            if value == observed_value:
                assigned_value = 1
            else:
                assigned_value = 0
            lambda_values[value] = assigned_value
            pi_values[value] = assigned_value
            cpd_key = Utils.get_cpd_key([observed_variable, observed_value], [])
            self._conditional_probabilities[cpd_key] = assigned_value

    def _update_network(self, evidence):
        observed_variable = evidence[0]
        observed_value = evidence[1]
        self._update_evidence_node_data(observed_variable, observed_value)

        #  Now we send lambda messages to all the parent
        #  nodes of the evidence node
        parents = self._bayesian_network.predecessors(observed_variable)
        for parent in parents:
            if parent not in self._evidence_set:
                self._send_lambda_message(observed_variable, parent)

        children = self._bayesian_network.successors(observed_variable)
        #  Now we send pi messages to the children of the evidence node
        for child in children:
            self._send_pi_message(observed_variable, child)

    def add_evidence(self, evidence):
        self._update_network(evidence)

    def get_probability(self, cpd_key):
        return self._conditional_probabilities[cpd_key]

    @staticmethod
    def test():
        bayesian_network = DiGraph()
        edges = [('A', 'C'), ('B', 'C'), ('C', 'D'), ('C', 'E'), ('D', 'F'), ('D', 'G')]
        bayesian_network.add_edges_from(edges)
        for node in bayesian_network.nodes():
            node_object = bayesian_network.node[node]
            #  All the variables are binary
            node_object['values'] = ['0', '1']

        conditional_probabilities = {
                                                'A1': 0.7,
                                                'A0':0.3,
                                                'B1': 0.4,
                                                'B0':0.6,
                                                'C1|A0,B0': 0.1, 'C1|A1,B0': 0.3,
                                                'C1|A0,B1': 0.5, 'C1|A1,B1': 0.9,
                                                'C0|A0,B0': 0.9, 'C0|A1,B0': 0.7,
                                                'C0|A0,B1': 0.5, 'C0|A1,B1': 0.1,
                                                'D1|C0': 0.8, 'D1|C1': 0.3,
                                                'D0|C0': 0.2, 'D0|C1': 0.7,
                                                'E1|C0': 0.2, 'E1|C1': 0.6,
                                                'E0|C0': 0.8, 'E0|C1': 0.4,
                                                'F1|D0': 0.1, 'F1|D1': 0.7,
                                                'F0|D0': 0.9, 'F0|D1': 0.3,
                                                'G1|D0': 0.9, 'G1|D1': 0.4,
                                                'G0|D0': 0.1, 'G0|D1': 0.6
                                     }
        inference = PearlsInference(bayesian_network, conditional_probabilities)
        print '-------------------------------'
        inference.add_evidence(['C', '1'])
        print '----------------------------------'
        inference.add_evidence(['A', '1'])
        pprint(conditional_probabilities)
        #  print inference.get_probability('B1|C1')

def main():
    PearlsInference.test()

if __name__ == '__main__':
    main()










