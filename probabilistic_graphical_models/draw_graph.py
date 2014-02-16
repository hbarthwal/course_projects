'''
Created on Dec 10, 2013

@author: himanshu
'''

from networkx import draw, DiGraph
import matplotlib.pyplot as plt
edges = [['A', 'L'],
['B', 'C'],
['B', 'D'],
['C', 'Q'],
['C', 'R'],
['E', 'I'],
['E', 'P'],
['F', 'I'],
['F', 'J'],
['G', 'E'],
['H', 'L'],
['I', 'M'],
['L' , 'T'],
['L', 'N'],
['N', 'P'],
['Q', 'S'],
['R', 'J'],
['T', 'K'],
['K', 'O']]

new_edges = []
for edge in edges:
    new_edge = []
    for node in edge:
        new_edge.append(str(ord(node) - ord('A')))
    new_edges.append(new_edge)

graph = DiGraph()
graph.add_edges_from(new_edges)
draw(graph)
plt.show()
