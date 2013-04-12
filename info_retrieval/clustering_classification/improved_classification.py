'''
Created on Apr 8, 2013

@author: Himanshu Barthwal
'''

from bing import DocumentsGenerator
from re import findall, UNICODE
from collections import Counter
from math import log
from operator import itemgetter
from stopwords import stopwords

class NaiveBayes:
    _bingDocsGenerator = None
    _queryList = ['bing', 'amazon', 'twitter', 'yahoo', 'google',
                     'beyonce', 'bieber', 'television', 'movies', 'music',
                     'obama', 'america', 'congress', 'senate', 'lawmakers']
    _categories = ['Entertainment', 'Business', 'Politics']
    _priors = {'Sports': 0.7} 
    _documentCollection = {'ab4b5bbcaef44446fc': {}}
    _termsMIDict = {}
    
    
    '''
    {'d_u_m_m_y$t_e_r_m': 'prior': {'Entertainment': .45, 'Business': .35,... }, }
    '''
           
    _termsDict = {}
    _noOfTermsToBeSelected = 9000
    
    def __init__(self, dataCacheFile):
        self._documentCollection.clear()
        self._priors.clear()
        self._bingDocsGenerator = DocumentsGenerator(dataCacheFile)
        self._populateDocuments()
        self._calculateProbabilities()
        self._calculateMutualInformation()
        self._pruneTermDict(self._noOfTermsToBeSelected)
        
    '''
    Here we do the feature selection
    
    '''
    def _pruneTermDict(self, numberOfTermsSelected):
        print 'Pruning terms'
        total = len(self._termsDict)
        print 'Number of features before pruning', total
        categoryTermMIDict = {}
        for category in self._categories:
            lstTermMI = []
            for term in self._termsMIDict:
                termMIInfo = self._termsMIDict[term]
                MI = termMIInfo[category]['MI']                
                lstTermMI.append((term, MI))
            categoryTermMIDict[category] = sorted(lstTermMI, key = itemgetter(1))
        
        termsToRemovePerCategory = (total - numberOfTermsSelected) / len(self._categories)   
        for category in self._categories:
            removedTerms = 0
            for termInfo in categoryTermMIDict[category]:
                term = termInfo[0]
                if removedTerms == termsToRemovePerCategory:
                    break
                
                if term in self._termsDict:
                    try:
                        print 'Removed ', term
                    except:
                        print 'error in printing!!'
                    self._termsDict.pop(term)
                removedTerms += 1
                    
        print 'Number of features after pruning', len(self._termsDict)

        
    def _removeStopWords(self, terms):
        for term in terms:
            if term in stopwords:
                terms.remove(term)
                
    def _populateDocuments(self):
        print 'Getting Documents for CLassification'
        jsonData = self._bingDocsGenerator.getDocuments(self._queryList, self._categories)
        print 'Got data !!'
        for documentJson in jsonData:
            docInfoDict = {}
            docId = documentJson['id']
            description = documentJson['description']
            title = documentJson['title']
            terms = findall('\w+', title + ' ' + description , UNICODE)
            docInfoDict = {}
            self._removeStopWords(terms)
            docInfoDict['terms'] = terms
            docInfoDict['termsSet'] = set(terms)
            docInfoDict['category'] = documentJson['category']
            self._documentCollection[docId] = docInfoDict
        print len(self._documentCollection), ' is the total number of documents'
                
    
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

    def _updateMutualInfoData(self):
        for term in self._termsDict:
            if term not in self._termsMIDict:
                self._termsMIDict[term] = {}
                for category in self._categories:
                    self._termsMIDict[term][category] = {'N11':0,'N10':0,'N00':0, 'N01':0}
                    
            for docId in self._documentCollection:
                document = self._documentCollection[docId]
                termsSet = document['termsSet']
                docCategory = document['category']
                
                if term in termsSet:
                    self._termsMIDict[term][docCategory]['N11'] += 1
                    
                    for category in self._categories:
                        if category == docCategory:
                            continue
                        self._termsMIDict[term][category]['N10'] += 1
                else:
                    self._termsMIDict[term][docCategory]['N01'] += 1
                        
                    for category in self._categories:
                        if category == docCategory:
                            continue
                        self._termsMIDict[term][category]['N00'] += 1
        
    def _updateTermsData(self, terms, category, docId):
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
                    # updating the information for the term in the terms Dictionary
                    self._termsDict[term] = termDataDict
               
    def _calculateMutualInformation(self):
        self._updateMutualInfoData()
        for term in self._termsMIDict:
            termDataDict = self._termsMIDict[term]
            for category in self._categories:
                N11 = float(termDataDict[category]['N11']) + 0.00001
                N10 = float(termDataDict[category]['N10']) + 0.00001
                N01 = float(termDataDict[category]['N01']) + 0.00001
                N00 = float(termDataDict[category]['N00']) + 0.00001
                N = N10 + N11 + N01 + N00
                N1 = N10 + N11
                N0 = N01 + N00
                MI = 0
                MI += (N11 / N) * log( (N * N11) / (N1 * N1), 2)
                MI += (N01 / N) * log( (N * N01) / (N0 * N1), 2)
                MI += (N10 / N) * log( (N * N10) / (N1 * N0), 2)
                MI += (N00 / N) * log( (N * N00) / (N0 * N0), 2) 
                termDataDict[category]['MI'] = MI
                
                
                
        
    def _calculateProbabilities(self):
        for docId in self._documentCollection:
            document = self._documentCollection[docId]
            docCategory = document['category']
            terms = document['terms']
            self._updatePriorData(docCategory)
            self._updateTermsData(terms, docCategory, docId)
        
        print 'Calculating probabilities'
        for priorCategory in self._priors:
            prior = self._priors[priorCategory] / float(len(self._documentCollection))
            self._priors[priorCategory] = prior
        
        for term in self._termsDict:
            termDataDict = self._termsDict[term]
            priorDict = termDataDict['prior']
            
            for priorCategory in priorDict:
                priorDict[priorCategory] = (priorDict[priorCategory] + 1) / (float(priorDict['totalCount']) + len(self._termsDict))
        
            
    def classifyDocument(self, document):
        title = document['title']
        description = document['description']
        terms = findall('\w+', title + ' ' + description , UNICODE)
        self._removeStopWords(terms)
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
            
        documentCategory = max(categoryProbabilities, key=itemgetter(1))[0]
        return documentCategory
       
    def displayData(self):
        print '**********************'
        for term in self._termsMIDict:
            termData = self._termsMIDict[term]
            try:
                print term,': ----> ', termData
            except:
                print 'Error !!'
            print '-------------------------'

        
    def testClassifier(self):
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
    print 'Main'
    classifier = NaiveBayes('nb.json')
    classifier.testClassifier()

if __name__ == "__main__":
    main()  
        
    
