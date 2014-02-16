'''
Created on Dec 11, 2013

@author: Himanshu Barthwal
'''

observed_data_directory = r'/home/himanshu/workspace/PGM/bnlearning/observed_data'
network_data_directory = r'/home/himanshu/workspace/PGM/bnlearning/network_data'
networks_settings = {
                                'genome': {
                                           'max_allowed_degree' : 4,
                                           'max_parents': 2,
                                            'max_children' : 2,
                                            'max_change_count': 10,
                                            'hyperparameter': 1,
                                            'tabu_list_size': 10,
                                            'data_set_size' :  1000
                                              },
                                }
