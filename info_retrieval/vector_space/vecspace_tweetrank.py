'''
Created on Mar 2, 2013

@author: hb
'''
from vector_space_retrieval import VectorSpace
from tweet_ranking import TweetUserRanking
from sys import stdin, argv
from operator import itemgetter
from string import replace
from pprint import pprint

class VectorSpaceAndUserRank:
    
    #weight for combining pagerank with vectorspace results
    beta = .4
    
    # object of the vector space retriever
    vsRanker = ''
    
    # object of the page ranker
    tweetRanker = ''
    
    def __init__(self, filename):
        print 'Creating Vector Space..'
        self.vsRanker = VectorSpace(filename)
        print 'Ranking users...'
        self.tweetRanker = TweetUserRanking(filename)
        
    # gets the users from the vector space query results
    def getUsersFromVsResults(self, vsResults):
        usersList = []
        for result in vsResults:
            usersList.append(result['username'])
        return usersList
         
    
    
    def processQuery(self, query):
        # fetch the top 100 results from vector space retrieval
        vsResults = self.vsRanker.processQuery(query, 200)
        if len(vsResults) == 0:
            return []
        # get the users from the result set 
        usersList = self.getUsersFromVsResults(vsResults)
        
        # arrange the users by their ranks
        userScoreDict = self.tweetRanker.getRankScoresForUsers(usersList)
        scoreDict = {}
        vsPageRankScoredResults = {}
        # now we caculate the product of zipfian ranks and cosine similaritiy 
        # for all results we got from vector space retrieval
        for vsResult in vsResults:
            rankScore = userScoreDict[vsResult['username']]
            finalScore = vsResult['cosineSimilarity'] * self.beta + (1 - self.beta) * rankScore
            result = {
                      'text' : vsResult['text'],
                      'username' : vsResult['username']
                      }
            vsPageRankScoredResults[vsResult['tweetId']] = result
            scoreDict[vsResult['tweetId']] = finalScore
        
        # sort the scoreDict by the finalScores 
        resultDict = sorted(scoreDict.items(), None , itemgetter(1) , True)
        
        finalresult = []
        for tweet in resultDict:
            #fill the final result dictionary with the results
            #finalRankScore = tweet[1]
            tweetId = tweet[0]
            tweetText =  vsPageRankScoredResults[tweetId]['text']
            finalresult.append(tweetText)
        
        finalresult = finalresult[:50]
        # return the top 50 results
        return finalresult


    def getVectorSpaceQueryResults(self, query, numResults):
        results = self.vsRanker.processQuery(query, numResults)
        resultingTweetTexts = []
        for result in results:
            resultingTweetTexts.append(result['text'])
        return resultingTweetTexts
    
    def getTopKUsers(self, K):
        results = self.tweetRanker.getTopKUsers(K)
        topKUserNames = []
        for result in results:
            topKUserNames.append(result[0])
        return topKUserNames
            
        
        

def main():
    filename = argv[1].strip()
    searchEngine = VectorSpaceAndUserRank(filename)
    print 'Hi! you can search here using the vector space retrieval'
    print 'and using both pagerank and vector space'
    print '1. If you want to see the vector space results just '
    print 'type "vssearch <query>" and enter key '
    print '2. For executing page rank + vector space search'
    print 'type "prvssearch <query>" and enter key'
    print '<query> is the search query like "mars google" etc.'
    print '3. Type "userrank" and enter key to view the top 50 users sorted by their ranks..'
    print '4. Type "quit" to  exit the program'
    print 'Enter Query Now !!'
    while True:
        query = stdin.readline()
        isVSSearch = 'vssearch' in query
        isPRVSSearch = 'prvssearch' in query
        isUserRankQuery = 'userrank' in query
        results = []
        if isPRVSSearch:
            query = replace(query,'prvssearch','')
            query = query.strip()
            if query == '':
                print 'Blank query try again ...'
                continue;
            print 'Executing Query..'
            results = searchEngine.processQuery(query.lower())
        
        
        elif isVSSearch:
            query = replace(query,'vssearch','')
            query = query.strip()
            if query == '':
                print 'Blank query try again ...'
                continue;
            print 'Executing Query..'
            results = searchEngine.getVectorSpaceQueryResults(query, 50)
        
        elif isUserRankQuery:
            results = searchEngine.getTopKUsers(50)
        
        elif 'quit' in query:
            print 'Goodbye !!'
            break
            
        else:
            print 'Please try again!!'
            continue
        if len(results) > 0 :
            index = 1
            for result in results:
                print index , ' - ' , result.encode('ascii', 'ignore')
                index += 1
            print('-----------------------------------------------------------------')
            
        else:
            print 'No results  :( '
            print 'Try Again!!'
    
if __name__ == '__main__':
    main()
    
        
        
        
        
        
        
        
        
