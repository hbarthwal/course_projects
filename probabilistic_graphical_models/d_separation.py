'''
Created on Oct 4, 2013
@author: Himanshu Barthwal

Homework 1, Problem 4
Probabilistic Graphical Models
'''
from networkx import DiGraph

'''
Provides the functionality of finding the d-separated nodes
in a given Bayesian Network with respect to a given
source node and evidence nodes.
'''    
class DSeparation:
    '''
    @param graph: The Bayesian Network for which the d-separated
    nodes are to be identified.
    
    @param observed_nodes: The nodes which are already observed
    or the evidence nodes.
    
    @param source_nodes: The node with respect to which the d-separated
    nodes are to be found out.
    '''
    def __init__(self, graph, observed_nodes, source_node):
        self._graph = graph
        self._observed_nodes = observed_nodes
        self._source_node = source_node
        # Ancestor set of the observed nodes.
        self._ancestors = []
        # Set of reachable nodes.
        self._reachable = []
        # Set of nodes to be visited.
        self._to_be_visited = [observed_node for observed_node in observed_nodes]
        # Set of visited nodes.
        self._visited = []
        
    '''
    Puts all the ancestors of the observed nodes in the "ancestors set".
    '''
    def _find_ancestors(self):
        while len(self._to_be_visited) > 0:
            node = self._to_be_visited.pop()
            if node not in self._ancestors:
                # Add the parents of node to the to_be_visited set
                for parent in self._graph.predecessors(node):
                    self._to_be_visited.append(parent)
            self._ancestors.append(node)

    def _add_parents(self, node):
        for parent in self._graph.predecessors(node):
            # Node's parents will be visited from bottom
            self._to_be_visited.append((parent, 'Up'))
            
    def _add_children(self, node):
        for child in self._graph.successors(node):
            # Node's children will be visited from top
            self._to_be_visited.append((child, 'Down'))
    
    '''
    Performs a breadth first search starting from the 
    given source node. Stops whenever an 'inactive' trail 
    is encountered.
    '''
    def _breadth_first_search(self):
        self._find_ancestors()
        # Traverse active trails starting from source_node        
        self._to_be_visited = [(self._source_node, 'Up')]
        while len(self._to_be_visited) > 0:
            (node, direction) = self._to_be_visited.pop()
            # if (node, direction) is not in visited set
            if (node, direction) not in self._visited:
                # if the node is not in observed set
                if node not in self._observed_nodes:
                    # The node is reachable so we add it to the
                    # reachable set
                    self._reachable.append(node)
                
                # We mark the (node, direction) as visited
                self._visited.append((node, direction))
                
                # Trail up through node is active if node is
                # not observed.
                if direction == 'Up' and node not in self._observed_nodes:
                    self._add_parents(node)
                    self._add_children(node)
                
                elif direction == 'Down':
                    #if the node is not in observed set
                    if node not in self._observed_nodes:
                        self._add_children(node)
                    if node in self._ancestors:
                        # V structure trails are active
                        self._add_parents(node)
    
    '''
    Entry point for the d-separation algorithm execution.
    '''
    def run_dseparation(self):
        self._breadth_first_search()

    '''
    Returns the list of d-separated nodes.
    '''
    def get_dseparated_nodes(self):
        return list(set(self._graph.nodes()) - set(self._reachable)- set(self._observed_nodes))
        

def add_nodes(graph):
    # Adding all the nodes
    graph.add_nodes_from(['A','B','C','D','E','F',
                          'G','H','I','J','K','L','M'])

def add_edges(graph):
    # Adding directed edges
    graph.add_edges_from([('A', 'D'),('B', 'D'),('D', 'G'),
                          ('D', 'H'),('H', 'K'),('G', 'K'),
                          ('H', 'E'),('C', 'E'),('E', 'I'),
                          ('I', 'L'),('F', 'I'),('F', 'J'),
                          ('J', 'M')])
'''
Creates the input graph for the D-separation algorithm
'''
def create_sample_graph():
    graph = DiGraph()
    add_nodes(graph)    
    add_edges(graph)
    return graph
    
def main():
    print 'Problem 3:'
    print '(a)'
    graph = create_sample_graph()
    
    problem_3_a = DSeparation(graph, 
                        observed_nodes = ['K','I'],
                        source_node = 'A')
    problem_3_a.run_dseparation() 
    print problem_3_a.get_dseparated_nodes()
    
    print '(b)'
    problem_3_b = DSeparation(graph, 
                        observed_nodes = ['D'],
                        source_node = 'G')
    problem_3_b.run_dseparation()    
    print problem_3_b.get_dseparated_nodes()
   
    print '(c)'
    problem_3_c = DSeparation(graph, 
                        observed_nodes = ['C','L'],
                        source_node = 'B')
    problem_3_c.run_dseparation()    
    print problem_3_c.get_dseparated_nodes()
    
    print '(d)' 
    problem_3_d = DSeparation(graph, 
                        observed_nodes = ['K','E'],
                        source_node = 'A')
    problem_3_d.run_dseparation()        
    print problem_3_d.get_dseparated_nodes()
    
    print '(e)'
    problem_3_e = DSeparation(graph, 
                        observed_nodes = ['L'],
                        source_node = 'B')
    problem_3_e.run_dseparation()    
    print problem_3_e.get_dseparated_nodes()
    
if __name__ == '__main__':
    main()

        
        
        
        
        
        
        
        
        
        