'''
Created on Apr 3, 2013

@author: Himanshu Barthwal
'''

from bing import DocumentsGenerator
from re import findall, UNICODE
from collections import Counter
from math import log
from operator import itemgetter

class NaiveBayes:
    _bingDocsGenerator = None
    _queryList = ['bing', 'amazon', 'twitter', 'yahoo', 'google',
                     'beyonce', 'bieber', 'television', 'movies', 'music',
                     'obama', 'america', 'congress', 'senate', 'lawmakers']
    _categories  = ['Entertainment', 'Business', 'Politics']
    _priors = {'Sports': 0.7} 
    _documentCollection = {'ab4b5bbcaef44446fc': {}}
    
    '''
    {'d_u_m_m_y$t_e_r_m': 'prior': {'Entertainment': .45, 'Business': .35,... }, }
    '''
           
    _termsDict = {}
    
    
    def __init__(self, dataCacheFile):
        self._documentCollection.clear()
        self._priors.clear()
        self._bingDocsGenerator = DocumentsGenerator(dataCacheFile)
        self._populateDocuments()
        self._calculateProbabilities()
         
    
    def _populateDocuments(self):
        print 'Getting Documents for learning Classification..'
        jsonData =  self._bingDocsGenerator.getDocuments(self._queryList, self._categories)
        for documentJson in jsonData:
            docInfoDict = {}
            docId = documentJson['id']
            description = documentJson['description']
            title = documentJson['title']
            terms = findall('\w+', title + ' ' + description , UNICODE)
            docInfoDict = {}
            docInfoDict['terms'] = terms
            docInfoDict['category'] = documentJson['category']
            self._documentCollection[docId] = docInfoDict
                
    
    def _updatePriorData(self, category):
        if category in self._priors:
            self._priors[category] += 1
        else:
            self._priors[category] = 0
        
    def _updateDataForTerm(self, term, category, termFrequency):
        termDataDict = self._termsDict[term]
        priorDataDict = termDataDict['prior']
        # updating term frequency
        priorDataDict[category] += termFrequency
        priorDataDict['totalCount'] += termFrequency 
    

    def _initializeTermData(self, category, termFrequency):
        # initializing prior data for the term
        termDataDict = {}
        termDataDict['prior'] = {}
        for categoryName in self._categories:
            termDataDict['prior'][categoryName] = 0
        
        termDataDict['prior']['totalCount'] = termFrequency
        termDataDict['prior'][category] = termFrequency
        return termDataDict

    def _updateTermsData(self, terms, category):
        termsSet = set(terms)
        termFrequencyDistribution = Counter(terms)
        for term in termsSet:
                termDataDict = {}
                termFrequency = termFrequencyDistribution[term]
               
                if term in self._termsDict:
                    termDataDict = self._termsDict[term]
                    self._updateDataForTerm(term, category, termFrequency)
                
                else:
                    termDataDict = self._initializeTermData(category, termFrequency)
                    self._termsDict[term] = termDataDict
                # updating the information the term in the terms Dictionary
                
        
    def _calculateProbabilities(self):
        for docId in self._documentCollection:
            document = self._documentCollection[docId]
            docCategory = document['category']
            terms = document['terms']
            self._updatePriorData(docCategory)
            self._updateTermsData(terms, docCategory)
            
        
        print 'Calculating probabilities'
        for priorCategory in self._priors:
            prior = self._priors[priorCategory] / float(len(self._documentCollection))
            self._priors[priorCategory] = prior
        
        for term in self._termsDict:
            termDataDict = self._termsDict[term]
            priorDict = termDataDict['prior']
            
            for priorCategory in priorDict:
                priorDict[priorCategory] = (priorDict[priorCategory] + 1 ) / (float(priorDict['totalCount']) + len(self._termsDict))
        
            
    def classifyDocument(self, document):
        title = document['title']
        description = document['description']
        terms = findall('\w+', title + ' ' + description , UNICODE)
        categoryProbabilities = []
        termProbabilityLogSum = 0 
        for category in self._categories:
            categoryProbability = 0
            termProbabilityLogSum = 0
            for term in terms:
                if term in self._termsDict:
                    termProbabilityLogSum += log(self._termsDict[term]['prior'][category], 2)
            categoryProbability = log(self._priors[category], 2) + termProbabilityLogSum 
            categoryProbabilities.append((category, categoryProbability))
            
        documentCategory = max(categoryProbabilities, key = itemgetter(1))[0]
        return documentCategory
       
    def displayData(self):
        for term in self._termsDict:
            termDataDict = self._termsDict[term]
            priorDict = termDataDict['prior']
            print term,' --> ', priorDict
        print '-------------------------'
        print self._priors
        
        
    def testClassifier(self):
        print 'Getting documents for testing'
        bingDocsFetcher = DocumentsGenerator('test.json')
        testQueries = ['apple', 'facebook', 'westeros', 'gonzaga', 'banana']
        categories = ['Entertainment', 'Business', 'Politics']
        jsonDocData = bingDocsFetcher.getDocuments(testQueries, categories)
        numDocs = len(jsonDocData)
        print numDocs, ' is the number of documents'
        confusionDict = {}
        for category in self._categories:
            confusionDict[category] = {}
            confusionDict[category]['TN'] = 0
            confusionDict[category]['TP'] = 0
            confusionDict[category]['FN'] = 0
            confusionDict[category]['FP'] = 0
            
        for document in jsonDocData:
            classPredicted = self.classifyDocument(document)
            actualClass = document['category']
            if actualClass == classPredicted:
                confusionDict[actualClass]['TP'] += 1
            
            else:
                confusionDict[actualClass]['FN'] += 1
                confusionDict[classPredicted]['FP'] += 1
                
        for category in self._categories:
            confusionDict[category]['TN'] = numDocs - confusionDict[category]['TP'] - confusionDict[category]['FP'] - confusionDict[category]['FN']
        
        (tpSum, fpSum, fnSum) = (0, 0, 0)
        
        for category in confusionDict:
            tpSum += confusionDict[category]['TP']
            fpSum += confusionDict[category]['FP']
            fnSum += confusionDict[category]['FN']
        
        precision = tpSum / float(tpSum + fpSum)
        recall = tpSum / float(tpSum + fnSum)
        
        f1 = 2 * precision * recall / (precision + recall)
        print 'Mico averaged F1 ', f1
        print confusionDict
        
 
def main():
    classifier = NaiveBayes('nb.json')
    classifier.testClassifier()
        
if __name__ == "__main__":
    main()  
        
    