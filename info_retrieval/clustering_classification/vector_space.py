'''
Created on Apr 3, 2013

@author: Himanshu Barthwal
'''
from exceptions import RuntimeError
from json import loads
from re import findall, UNICODE 
from collections import Counter, OrderedDict
from time import time
from math import log, pow
from stopwords import stopwords
from pprint import pprint
from django.conf.locale import de
from Crypto.Cipher import DES

class VectorSpace :
    
    ''' 
    Contains the data for the documents like text, list of unique terms, set of terms
    and the vector magnitude of the document in the vector space
    '''
    _documentsDict = {72348234:{'termsSet':(['nkjd', 'adfah']), 'vectorMagnitude' : 24.67}, 'vector':[]}    
    
    '''
    Contains information particular to a term, like term documentid : frequency mapping and
    inverse document frequency
    
    {'d_u_m_m_y$t_e_r_m': {'idf' : 2.09,   86472348234 : 5.94} , dimensionalIndex : 1}
                term :     { 'idf': idf_value , documentID : termFrequency, 
                             'dimensionalIndex': dimensionalIndexValue}
    '''
           
    _termsDict = OrderedDict()
    
    _titleWeight = 1
    _applyWeighting = False
    '''
    We perform all the calculations when this class is instantiated
    '''
    def __init__(self, jsonData, removeStopWords = False, applyWeighting = False):
        self._parseJson(jsonData, removeStopWords)
        self._applyWeighting = applyWeighting
        self._populateTermsDictionary()
        self._calculateTFIDFVectors()
        self._normalizeVectors()
        print 'Dimension Count : ', len(self._termsDict)
    
    '''     
    This function iterates over all the documents and populates
    _termsDict with the documentFrequency and logarithmically scaled 
    termfrequency
    '''  
    def _populateTermsDictionary(self):
        dimensionalIndex = 0
        for docId in self._documentsDict:
            termsList = self._documentsDict[docId]['terms']
            termFrequencyDistribution = Counter(termsList)
            termsSet = self._documentsDict[docId]['termsSet']
            
            for term in termsSet:
                termDataDict = {}
                termFrequency = 1 + log(termFrequencyDistribution[term], 2)
               
                if term in self._termsDict:
                    termDataDict = self._termsDict[term]
                    # storing term frequency and term document frequency for each document
                    termDataDict[docId] = termFrequency
                    # the document frequency is incremented for 'term' on encountering it  
                    # in a given document
                    termDataDict['termDocFrequency'] = termDataDict['termDocFrequency'] + 1
                
                else:
                    # We enter initial values for the 'term' in the termDataDict
                    termDataDict = {'termDocFrequency': 1, docId : termFrequency, 'dimensionalIndex' : dimensionalIndex}
                    dimensionalIndex += 1
                
                # updating the information for all the terms in the given document
                self._termsDict[term] = termDataDict
       
     
    def _removeStopWords(self, terms):
        for term in terms:
            if term in stopwords:
                terms.remove(term)   
                
                
    '''
    This function parses the document corpus and 
    populates the documentDict with the text, terms and termsSet
    for a particular documentid
    '''
    def _parseJson(self, jsonData, removeStopWords):
        self._documentsDict.clear()
        for documentJson in jsonData: 
            docId = documentJson['id']
            description = documentJson['description']
            title = documentJson['title']
            document = title + ' ' + description 
            terms = findall('\w+', document , UNICODE)
            docInfoDict = {}
            if removeStopWords:
                self._removeStopWords(terms)
            docInfoDict['titletermsSet'] = set(findall('\w+', title , UNICODE))
            docInfoDict['terms'] = terms
            docInfoDict['termsSet'] = set(terms)
            docInfoDict['class'] = documentJson['query']
            self._documentsDict[docId] = docInfoDict
      
    '''  
    This function calculates the idf and scales it logarithmically
    '''
    def _calculateIDF(self):
        # total number of documents (or documents)
        docCount = len(self._documentsDict)
        for term in self._termsDict: # the total number of times 'term' occurs in the document
            termDocCount = self._termsDict[term].pop('termDocFrequency')
            if (termDocCount != 0): # inverse document frequency
                rawIdf = docCount / float(termDocCount) # logarithmically scale inverse document frequency
                self._termsDict[term]['idf'] = log(rawIdf, 2)

    def _calculateTFIDFVectors(self):
        self._calculateIDF()
        numVectorSpaceDimensions = len(self._termsDict)
        for docId in self._documentsDict:
            vector = [0] * numVectorSpaceDimensions
            docInfoDict = self._documentsDict[docId]
            for term in docInfoDict['termsSet']:
                dimensionalndex = self._termsDict[term]['dimensionalIndex']
                termFrequency = self._termsDict[term][docId]
                
                if self._applyWeighting and term in docInfoDict['titletermsSet']:
                    termFrequency *= self._titleWeight
                
                inverseDocFrequency = self._termsDict[term]['idf']
                vectorComponent = termFrequency * inverseDocFrequency
                vector[dimensionalndex] =  vectorComponent
            self._documentsDict[docId]['vector'] = vector
            
            
    def _normalizeVectors(self):
        for docId in self._documentsDict:
            vector = self._documentsDict[docId]['vector']
            vectorMagnitude = self.getVectorMagnitude(vector)
            componentIndex = 0
            for component in vector:
                component = component / vectorMagnitude
                vector[componentIndex] = component
                componentIndex += 1
                
         
    '''            
    This function calculates the vector magnitude for the documents
    ''' 
    def getVectorMagnitude(self, vector):
        vecMagnitude = 0
        # iterate over each component in a document vector 
        # and calculate the vector magnitude
        for component in vector:
            # summing up squares for each term in the vector
            vecMagnitude = vecMagnitude + pow (component, 2)
        return pow(vecMagnitude, 0.5)
        
    def getDotProductOfDocumentVectors(self, docVector1, docVector2):
        numVectorSpaceDimensions = len(self._termsDict)
        if len(docVector1) != len(docVector1):
            raise RuntimeError("Dimensional mismatch!!")
        dotProduct = 0
        for index in range(numVectorSpaceDimensions):
            dotProduct += docVector1[index] * docVector2[index]
        return dotProduct
    
    def getCosineSimilarity(self,  docVector1, docVector2):
        if len(docVector1) != len(docVector2):
            raise RuntimeError("Dimensional mismatch!!")
        dotProduct = self.getDotProductOfDocumentVectors(docVector1, docVector2)
        vectorMagnitudeDoc1 = self.getVectorMagnitude(docVector1)
        vectorMagnitudeDoc2 = self.getVectorMagnitude(docVector2)
        cosineSimilarity = dotProduct / (vectorMagnitudeDoc1 * vectorMagnitudeDoc2)
        return cosineSimilarity
    
    def getEuclidianDistance(self, docVector1, docVector2):
        numVectorSpaceDimensions = len(docVector1)
        if len(docVector1) != len(docVector2):
            raise RuntimeError("Dimensional mismatch!!")
     
        distance = 0
        for index in range(numVectorSpaceDimensions):
            distance += pow(docVector1[index] - docVector2[index], 2)
        distance = pow(distance , 0.5)
        return distance
        
    def getCentroid(self, docVectorList):
        if len(docVectorList) == 0:
            raise RuntimeError("Empty vector list!!")
        numVectorSpaceDimensions = len(docVectorList[0])
        meanVector = [0] * numVectorSpaceDimensions
        for index in range(numVectorSpaceDimensions):
            sumVectorComponent = 0
            for docVector in docVectorList:
                if len(docVector) != numVectorSpaceDimensions:
                    raise RuntimeError("Dimensional mismatch!!")
                sumVectorComponent += docVector[index]
            meanVector[index] = float(sumVectorComponent) / len(docVectorList)
        return  meanVector
    
    def getDocumentVector(self, docId):
        return self._documentsDict[docId]['vector']
    
    def getAllDocumentVectors(self):
        docVectorList = []
        for docId in self._documentsDict:
            docVectorList.append({'vector' : self._documentsDict[docId]['vector'],
                                  'class': self._documentsDict[docId]['class']})
        return docVectorList
    
    def _areEqual(self, docVector1, docVector2):
        numVectorSpaceDimensions = len(docVector1)
        for index in range(numVectorSpaceDimensions):
            if docVector1[index] != docVector2[index]:
                return False
        return True
        
def main():
    jsonFilename = '/tmp/data.json'  # argv[1]
    start = time()
    vecSpace = VectorSpace(loads(open(jsonFilename).read()))
    print 'It took' , time() - start , 'seconds to create vector space'
    docVector1 = [1,1,1]
    docVector2 = [3,3,3]
    centroid = vecSpace.getCentroid([docVector1, docVector2])
    distance = vecSpace.getEuclidianDistance(docVector1, docVector2)
    print 'Centroid :', centroid,' Distance: ', distance
  
if __name__ == '__main__':
    main()