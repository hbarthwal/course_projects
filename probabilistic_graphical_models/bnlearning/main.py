'''
Created on Dec 10, 2013

@author: himanshu
'''

from bn_skeleton import PC
from greedy_hill_climbing import GreedyHillClimber
from settings import networks_settings
from networkx import draw
import matplotlib.pyplot as plt


pc = PC('genome')
pc.perform_PC()
bn = pc.get_skeleton()
ns = networks_settings['genome']
gch = GreedyHillClimber(1 , bn, ns['tabu_list_size'], ns['max_change_count'])
print 'Performing GHC'
gch.perform_GHC()
graph = gch.get_solution()
draw(graph)
plt.show()

