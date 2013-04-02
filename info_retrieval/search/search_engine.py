'''
Created on Feb 5, 2013

@author: Preeti Suman
'''
import pickle, sys, re
from os import listdir
from os.path import isfile, join
from sys import stdin

class TextSearchEngine:
    # word : set(docID : list of positions)
    dictionary = {'preetisuman':{0 : []}}
    permutermIndex = {'':''}
    directory = ''
    
    def __init__(self, DocumentDir): 
        self.directory = DocumentDir
        self.WordsInDictionay()
    
    def WordsInDictionay(self):
        print 'Please wait while files are indexed'
        FilesNames = []
        try:
            for f in listdir(self.directory):
                if isfile(join(self.directory, f)) and '.txt' in join(self.directory, f):
                    FilesNames.append(f)
        except:
            print 'file not found'
            
        try:
            for FileName in FilesNames:
                print 'Indexing' , FileName
                self.DictUpdateFromFile(FileName)
            print '\n'
        except:
            print "Error occurred : ", sys.exc_info()
        print 'Done!!'
            
    def FetchTerms(self, TextContents):
        Content = TextContents.lower()
        tokens = re.findall("\w+", Content)
        return tokens
        
    def DictUpdateFromFile(self, FileName):
        Content = open(join(self.directory, FileName)).read()
        terms = self.FetchTerms(Content)
        docId = FileName
        position = 0
        
        # populating permuterm index
        for term in terms:
            term = term.lower()
            temp_term = term + '$'
            length = len(temp_term)
            for rotation_length in range(1, length + 1):
                temp_term = temp_term[rotation_length:] + temp_term [:rotation_length]
                self.permutermIndex[temp_term] = term
        # populating the dictionary
        for term in terms:
            doc_dict = {}
            
            if self.dictionary.has_key(term):
                doc_dict = self.dictionary[term]
                
                if doc_dict.has_key(docId):
                    doc_dict[docId].append(position)
                
                else:
                    doc_dict[docId] = [position]
                    self.dictionary[term] = doc_dict
            else :
                doc_dict[docId] = [position]
                self.dictionary[term] = doc_dict
                 
            position = position + 1
    
    def _getBooleanResults(self, query):
        terms = self.FetchTerms(query) 
        results = set()
        temp_result = set()
        try:
            for index in range(len(terms)):
                temp_result = set(self.dictionary[terms[index]])
                if index == 0:
                    results = temp_result
                else:
                    results = set(temp_result).intersection(results)
        except :
            results = set()
        return results
    
    def _getPhraseQueryResults(self, phrase_queries):
        results = set()
        temp_result = set()
        for phrase_query in phrase_queries:
            boolean_results = self._getBooleanResults(phrase_query)
            temp_result = self.processResultsForPhraseQuery(phrase_query, boolean_results)
            if results == set():
                results = temp_result
                continue
            results = results.intersection(temp_result)
        return results
    
    def getTermPositionsList(self, terms, docId):
        temp_position_list = []
        termIndex = 0
        for term in terms:
            termIndex = termIndex + 1
            temp_position_list.append(self.dictionary[term][docId])
        return temp_position_list
    
    def normalizePositions(self, positionList):
        offset = 0
        temp_position_list = []
        for positions in positionList:
            positions = [p - offset for p in positions]
            temp_position_list.append(positions)
            offset = offset + 1
        return temp_position_list
    
    def processResultsForPhraseQuery(self, query, boolean_results):
        phrase_results = []
        terms = self.FetchTerms(query)  
        for docId in boolean_results:
           
            term_position_list = self.getTermPositionsList(terms, docId)
            term_position_list = self.normalizePositions(term_position_list) 
            
            prev_positions_set = set(term_position_list[0])
            
            for positions in term_position_list:
                positions_set = set(positions)
                positions_set = positions_set.intersection(prev_positions_set)
                # intersection of the normalized postion lists wil give the 
                # [[3,5,8], [1,6,10]] --normalization--> [[3,5,8] ^ [0,5,9]] 
                prev_positions_set = positions_set
            if(positions_set != set([])):
                phrase_results.append(docId)
        return set(phrase_results)
    
    def permuteWildcardTerm(self, term):
        term = term + '$'
        shiftIndex = term.find('*') + 1
        return term[shiftIndex:] + term[:shiftIndex]   

    def _getWildCardQueryResults(self, wildcard_terms):
        wildcard_results = set()
        for query_term in wildcard_terms:
            permuterm = ''.join(self.permuteWildcardTerm(query_term))
            permuterm = permuterm [:-1]
            matched_terms = [self.permutermIndex[key] for  key in self.permutermIndex.keys() if  permuterm in key ]
            result_sets = [set(self.dictionary[matched_term]) for matched_term in matched_terms]
            final_result_set = set()
            for result_set in result_sets:
                final_result_set = final_result_set.union(result_set)
            if wildcard_results == set():
                wildcard_results = final_result_set
            else:
                wildcard_results = wildcard_results.intersection(final_result_set)
            
        return wildcard_results 
         
    def _writeIndexesToFile(self):
        with open('index.indx', 'wb') as handle:
            pickle.dump(self.dictionary, handle)
    
    def getWildCardTerms(self, terms):
        wildCardTerms = []
        for term in terms:
            if(term.find('*') != -1):
                wildCardTerms.append(term)
        return wildCardTerms    
        
    def getBooleanQueryTerms(self, terms):
        booleanQueryTerms = []
        for term in terms:
            if '*' not in term and term.find('"') == -1:
                booleanQueryTerms.append(term)
        return booleanQueryTerms   
    
    def _getResults(self, query):
        terms = query.split(' ')
        result = set()
        wildcard_results = set()
        phrase_query_results = set()
        boolean_results = set()
        wildcard_terms = self.getWildCardTerms(terms)
        phrase_queries = re.findall('"\s*((?:\w(?!\s+")+|\s(?!\s*"))+\w)\s*"', query)
        boolean_terms = self.getBooleanQueryTerms(terms)
        print phrase_queries
        
        if phrase_queries != []:
            phrase_query_results = self._getPhraseQueryResults(phrase_queries)
            
        if boolean_terms != []:
            boolean_results = self._getBooleanResults(' '.join(boolean_terms))
       
        if wildcard_terms != []:
            wildcard_results = self._getWildCardQueryResults(wildcard_terms)
           
        if boolean_terms != []:
            if phrase_queries != []:
                if wildcard_terms != []:
                    result = phrase_query_results.intersection(boolean_results).intersection(wildcard_results)
                else:
                    result = phrase_query_results.intersection(boolean_results)
            else:
                if wildcard_terms != []:
                    result = wildcard_results.intersection(boolean_results)
                else:
                    result = boolean_results
        else:
            if phrase_queries != []:
                if wildcard_terms != []:
                    result = phrase_query_results.intersection(wildcard_results)
                else:
                    result = phrase_query_results
            else:
                if wildcard_terms != []:
                    result = wildcard_results
               
        return result
     
  
def main():
    print sys.argv
    se = TextSearchEngine('E:\\Eclipse Workspace\\IRhomework1\\src\\ir\\homeworks\\first\\docs')
    se._writeIndexesToFile()
    print "Please enter a query!! Type 'Exxit' to Exit"
    while True:
        query = stdin.readline()
        query = query.strip().lower()
        if query == 'exxit':
            break
        result_set = se._getResults(query)
        if result_set != set():
            print list(result_set)
        else:
            print 'No Results found'
    print 'Bye!'
    return

if __name__ == '__main__':
    main()
