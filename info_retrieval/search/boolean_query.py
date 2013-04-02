'''
Created on Feb 4, 2013

@author: Himanshu Barthwal
'''

import sys
import re


class BooleanSearchEngine:
    dictionary = {'qqqq' : set([-1,-2])}
    
    def _populateDictionary(self, filenames):
        try:
            for filename in filenames:
                self.updateDictionary(filename)
        except:
            print "Error occurred : ", sys.exc_info()
            
    def getTerms(self, rawContent):
        tokens = re.findall("\w+", rawContent)
        return tokens

    def getDocId(self, filename):
        return filename.split('.')[0];
    
    def updateDictionary(self, filename):
        content = open(filename).read()
        terms = self.getTerms(content)
        for term in terms:
            term = term.lower()
            docId = self.getDocId(filename)
            if self.dictionary.has_key(term):
                self.dictionary[term].add(docId)
            else :
                self.dictionary[term] = set([docId]) 
    
    def _getResults(self, query):
        terms = self.getTerms(query)
        results =   self.dictionary[terms[0]]
        for term in terms:
            results =  self.dictionary[term].intersection(results)
        return results
    
    def _displayDictionary(self):
        print self.dictionary