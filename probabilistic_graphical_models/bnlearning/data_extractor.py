'''
Created on Dec 9, 2013

@author: Himanshu Barthwal
'''
from json import loads
from csv import reader
from pprint import pprint
from utils import FileUtils

class DataExtractor:
    '''
    Parses the files in a given directory
    and populates the data in dictionaries.
    '''
    def __init__(self, network_name, format = 'csv'):
        self._network_name = network_name
        self._data_vectors = {}
        self._variables_values_set = {}
        self._parse_files(format)
        self._data_length = 0

    def _parse_files(self, format):
        #  Iterate over all the files in the data directory and
        #  parse each one of them
        self._extract_data(format)
        self._extract_values_set()


    def get_csv_data(self, file):
        csv_reader = reader(file, delimiter = ' ')
        row_count = 0
        headers = []
        for row in csv_reader:
            if row_count == 0:
                for variable in row:
                    self._data_vectors[variable] = []
                    headers.append(variable)
                row_count += 1
            else:
                header_count = 0
                for data in row:
                    self._data_vectors[headers[header_count]].append(data)
                    header_count += 1

    def _extract_data(self, format):
        '''
        Parses the generated data file and populates the data into a dictionary.
        '''
        data_filename = FileUtils.get_observed_data_filename(self._network_name)
        with open(data_filename) as file:
            self.get_csv_data(file)
            if format == 'json':
                #  Now we convert the data to json format
                keys = self._data_vectors.keys()
                data_length = len(self._data_vectors[keys[0]])
                data_dict_list = []
                for i in xrange(data_length):
                    data_dict = {}
                    for j in xrange(len(keys)):
                        data_dict[keys[j]] = self._data_vectors[keys[j]][i]
                    data_dict_list.append(data_dict)
                self._data_vectors = data_dict_list


    def _extract_values_set(self):
        '''
        Loads the node data from the ground truth network file and
        fetches the values
        '''
        bayesian_network_filename = FileUtils.get_network_filename(self._network_name)
        nodes_data = None
        with open(bayesian_network_filename) as file:
            data = file.read()
            nodes_data = loads(data)

        for node in nodes_data['Vdata']:
            self._variables_values_set[node] = nodes_data['Vdata'][node]['vals']

    def get_data_vectors(self):
        '''
        Returns data vector dictionary, every file is considered to
        be a single independent dataset and the corresponding data vectors 
        are mapped to the filename as the key. 
        
        Each data vector conceptually represents a vector of values of all the 
        variables in the bayesian network. But here we have veritcally sliced the
        data vectors to make it easier for score calculations.    
        So each variable name is mapped with the values of the variable in all
        the data vectors.
        '''
        return self._data_vectors

    def get_variable_values_sets(self):
        '''
        Returns a dictionary which maps the variable name to a set of values
        which the variable can take. Here we are assuming that the data covers 
        each possible value of the variable atleast once.       
        '''
        return self._variables_values_set

    @staticmethod
    def test():
        '''
        Test method for the data extractor 
        Makes sure data is good .;)
        '''
        data = DataExtractor('genome')
        values_set = data.get_variable_values_sets()
        data_vectors = data.get_data_vectors()
        print data_vectors
        pprint(values_set)

def main():
    DataExtractor.test()

if __name__ == '__main__':
    main()
