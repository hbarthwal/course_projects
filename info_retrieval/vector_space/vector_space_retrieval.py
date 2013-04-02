# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 16:14:44 2013

@author: Himanshu Barthwal
"""
from json import loads
from re import findall, UNICODE 
from collections import Counter, OrderedDict, defaultdict
from time import time
from math import log, pow
from operator import itemgetter


class VectorSpace :
    
    #--------------------------------------------------------------------------------
    # contains the data for the tweets like text, list of unique terms, set of terms
    # and the vector magnitude of the tweet in the vector space
    tweetsDict = {72348234:{'termsSet':(['nkjd', 'adfah']), 'vectorMagnitude' : 24.67}}    
    
    # contains information particular to a term, like term tweetid : frequency mapping and
    # inverse document frequency
           
    termsDict = OrderedDict()
    # {'d_u_m_m_y$t_e_r_m': {'idf' : 2.09,   86472348234 : 5.94} }
    #            term :     { 'idf': idf_value , tweetID : termFrequency
    
    #------------------------------------------------------------------------------------
    
    # we perform all the calculations when this class is
    # instanciated
    def __init__(self, filename):
        self.parseJson(filename)
        self.populateTermsDictionary()
        self.calculateIDF()
        self.computeVectorMagnitudeforTweets()
     
        
    # this function iterates over all the tweets and populates
    # termsDict with the documentFrequency and logarithmically scaled 
    # termfrequency  
    def populateTermsDictionary(self):
        for tweetId in self.tweetsDict:
            termsList = self.tweetsDict[tweetId]['terms']
            termFrequencyDistribution = Counter(termsList)
            termsSet = self.tweetsDict[tweetId]['termsSet']
            
            for term in termsSet:
                termDataDict = {}
                termFrequency = 1 + log(termFrequencyDistribution[term], 2)
                if term in self.termsDict:
                    termDataDict = self.termsDict[term]
                    # storing term frequency and term document frequency for each tweet
                    termDataDict[tweetId] = termFrequency
                    # the document frequency is incremented for 'term' on encountering it  
                    # in a given tweet
                    termDataDict['termDocFrequency'] = termDataDict['termDocFrequency'] + 1
                
                else:
                    # We enter initial values for the 'term' in the termDataDict
                    termDataDict = {'termDocFrequency': 1, tweetId : termFrequency}
                
                # updating the information for all the terms in the given tweet
                self.termsDict[term] = termDataDict


    # this function parses the tweet corpus and 
    # populates the tweetDict with the text, terms and termsSet
    # for a particular tweetid
    def parseJson(self, filename):
        self.tweetsDict.clear()
        with open(filename) as fileData:
            for tweet in fileData:
                temp_json_dict = loads(tweet.lower())
                tweetId = temp_json_dict['id']
                terms = findall('\w+', temp_json_dict['text'] , UNICODE)
                json_dict = {}
                json_dict['terms'] = terms
                json_dict['text'] = temp_json_dict['text'] 
                json_dict['username'] = temp_json_dict['user']['screen_name']
                termsSet = set(terms)
                json_dict['termsSet'] = termsSet
                self.tweetsDict[tweetId] = json_dict
      
      
    # this function calculates the idf and scales it logarithmically
    def calculateIDF(self):
        # total number of documents (or tweets)
        docCount = len(self.tweetsDict)
        for term in self.termsDict: 
            # the total number of times 'term' occurs in the document
            termDocCount = self.termsDict[term].pop('termDocFrequency')
            if(termDocCount != 0):
                # inverse document frequency
                rawIdf = docCount / float(termDocCount)
                # logarithmically scale inverse document frequency
                self.termsDict[term]['idf'] = log(rawIdf, 2)
        
    # this function calculates the vector magnitude for the tweets 
    def computeVectorMagnitudeforTweets(self):
        # iterate over each tweet to calculate the vector magnitude
        # for all of them
        for tweetId in self.tweetsDict:
            termsSet = self.tweetsDict[tweetId]['termsSet']
            vecMagnitude = 0
            # iterate over each unique term in a particular tweet 
            # and calculate the vector magnitude
            for term in termsSet:
                # tfidf for each term in the tweet
                tfidf = self.termsDict[term]['idf'] * self.termsDict[term][tweetId]
                vecMagnitude = vecMagnitude + pow (tfidf, 2)
            self.tweetsDict[tweetId] ['vectorMagnitude'] = pow(vecMagnitude, 0.5)
   
    # calculates the vector magnitude of the query     
    def getQueryMagnitude(self, terms):
        queryMagnitude = 0
        # calculate the vectormagnitude for the  query
        termFrequencyDistribution = Counter(terms)
        for term in terms :
            if term in self.termsDict:
                # logarithmically scaled termfrequency
                termFrequency = (1 + log(termFrequencyDistribution[term], 2))
                
                tfidfValueForTerm = self.termsDict[term]['idf'] * termFrequency
                # incrementing the sum of squares of the tfidf terms
                queryMagnitude = queryMagnitude + pow(tfidfValueForTerm, 2)
                
        # taking the square root of the sum of squares of the tfidf terms gives
        # the magnitude
        queryMagnitude = pow(queryMagnitude, 0.5)
        return queryMagnitude
        
    def getCosineSimilarityOfQueryAndTweets(self, queryTerms):
        # the final dictionary which will hold the cosine similarities for 
        # all the (query, tweet) pairs
        tweetIdvsTFIDFDict = defaultdict()
       
        # calculating magnitude for the query vector
        queryMagnitude = self.getQueryMagnitude(queryTerms)
        termFrequencyDistribution = Counter(queryTerms)
        
        # calculate the cosine similarity for each term in a given tweet
        # and then add them up to calculate the overall cosine similarity
        # for the (query, tweet) pairs
        for term in queryTerms:
            if term in self.termsDict:
                termDataDict = self.termsDict[term]
                idfValueForTerm = termDataDict.pop('idf') 
                termFrequency = (1 + log(termFrequencyDistribution[term], 2))
                tfidfValueForTerm = idfValueForTerm * termFrequency
                
                # in one iteration of this loop the tweetIdvsTFIDFDict
                # gets cosine scores for a termcomponent with all the tweets
                for tweetId in termDataDict:
                    # calculation for 'term' with a given tweet
                    tweetComponent = (termDataDict[tweetId] * idfValueForTerm) / self.tweetsDict[tweetId]['vectorMagnitude']
                    queryComponent = tfidfValueForTerm / queryMagnitude 
                    termComponent = tweetComponent * queryComponent
                    
                    # we update the tweet's cosine score in the  tweetIdvsTFIDFDict dictionary
                    if tweetId in tweetIdvsTFIDFDict:
                        tweetIdvsTFIDFDict[tweetId] = tweetIdvsTFIDFDict[tweetId] + termComponent
                    else:
                        tweetIdvsTFIDFDict[tweetId] = termComponent
                    # Here we normalize the tfidf vector for the tweet
                    
                # since we popped the idf so we put it back here
                self.termsDict[term]['idf'] = idfValueForTerm
        return tweetIdvsTFIDFDict

    # gets the ordered results for a given 'query'

    def processQuery(self, query, numResults):
        queryTerms = findall('\w+', query.lower(), UNICODE)
        tweetIdvsTFIDFDict = self.getCosineSimilarityOfQueryAndTweets(queryTerms)
        results = sorted(tweetIdvsTFIDFDict.items(), None , itemgetter(1) , True)
        resultList = []
        for i in range(len(results)):
            if i >= numResults:
                break
            result = results[i]
            resultList.append({
                               'text' : self.tweetsDict[result[0]]['text'],
                               'tweetId': result[0],
                               'cosineSimilarity' : result[1],
                               'username' : self.tweetsDict[result[0]]['username']
                             })
        return resultList
        
def main():
    jsonFilename = 'E:\Padhai\IR\Homework\HW2\mars_tweets_medium.json'  # argv[1]
    start = time()
    tfidfObj = VectorSpace(jsonFilename)
    print 'It took' , time() - start , 'seconds to create vector space'
    resultSet = tfidfObj.processQuery('google', 50)
    print resultSet
   

if __name__ == '__main__':
    main()
