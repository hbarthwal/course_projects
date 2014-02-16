'''
Created on Dec 10, 2013

@author: himanshu
'''
import json
from networkx import DiGraph, draw
from libpgm.nodedata import NodeData
from libpgm.graphskeleton import GraphSkeleton
from libpgm.discretebayesiannetwork import DiscreteBayesianNetwork
from libpgm.pgmlearner import PGMLearner
import matplotlib.pyplot as plt
from data_extractor import DataExtractor


#  generate some data to use
data_ext = DataExtractor('genome', format = 'json')
data = data_ext.get_data_vectors()
print 'Got data with ', len(data), ' vectors'
#  instantiate my learner
learner = PGMLearner()

print 'learning the structure'
#  estimate structure
result = learner.discrete_constraint_estimatestruct(data, pvalparam = 0.02)

#  output
print json.dumps(result.E, indent = 2)
graph = DiGraph()
graph.add_edges_from(result.E)
draw(graph)
plt.show()
