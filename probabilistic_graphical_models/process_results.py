'''
Created on Dec 10, 2013

@author: himanshu
'''
from csv import reader
from string import strip
from random import random

with open(r'pgmoutputfiles/table_test50d.txt', 'r') as file:
    csv_reader = reader(file, delimiter = ' ')
    row_count = 0
    data_dict = {}
    for row in csv_reader:
        if len(row) == 0:
            break
        variable = strip(row[0])
        if variable not in data_dict:
            data_dict[variable] = []

        actual_value = strip(row[1])
        predicted_value = strip(row[2])
        prob = round(float(strip(row[3])), 3)
        prob = float(strip(row[3])) + random() / 100
        data_dict[variable].append((actual_value, predicted_value, prob))

for variable in data_dict:
    print variable, ': ', data_dict[variable]





