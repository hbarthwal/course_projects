'''
Created on Feb 26, 2013

@author: Himanshu Barthwal
'''

from json import loads
from collections import OrderedDict
from time import time
from operator import itemgetter

# this class is responsible for ranking the tweet users

class TweetUserRanking:
    #-----------------------------------------------------------------------
    # set of users mentioning someone except just themselves
    # ie. if a user just mentions herself then she is ignored
    setMentioners = set()
    
    # set of users mentioned by someone
    setMentionees = set()

    # maintains the mapping of the users and the mentioned users
    usersMentionsMap = {'user1': ['mentioned user 1', 'mentioned user 2']}
    
    # set of users used to create the 'vectorUserMap' 
    setUsers = set()
    
    # this map maintains the users' order in the matrix space
    # as well as the pagerank of the users at a given point of time
    # it is the primary data structure used to  
    # calculate the pagerank iteratively
    vectorUserMap = OrderedDict() 
    
    
    # the constant value used to combine the link matrix 
    # and the teleportation factor
    alpha = .9
    
    # error tolerance value for page rank calculation
    maxerror = .000001
    
    # this list holds the final output of the algorithm
    # the order of the users in this list depict their ranking
    rankedUsers = []
    #-----------------------------------------------------------------------
    
    
    # we perform all the calculations when this class is
    # instanciated
    def __init__(self, filename):
        self.usersMentionsMap.clear()
        self.parseJson(filename)
        self.pruneUserMentionMap()
        self.processUsers()
        self.calculatePageRank()
        self.rankAllUsers()
    
   
    def normalizePageRanks(self):
        sum = 0
        # we normalize the pagerank values
        for user in self.vectorUserMap:
            sum += self.vectorUserMap[user][1]
        
        for user in self.vectorUserMap:
            self.vectorUserMap[user][1] = self.vectorUserMap[user][1] / sum

    # in this function we calculate page rank using the 
    # out bound links 

    def calculatePageRank(self):
        while True:
            N = len(self.vectorUserMap)
            # this part deals with distriuting the page rank
            # to all the outbound users from a particular user
            for mentioner in self.usersMentionsMap:
                if(mentioner in self.vectorUserMap):
                    mentionees = self.usersMentionsMap[mentioner]
                    mentioneesCount = len(mentionees)
                    for mentionee in mentionees:
                        if(mentionee in self.vectorUserMap):
                            self.vectorUserMap[mentionee][2] += (self.vectorUserMap[mentioner][1] / float(mentioneesCount))
     
            # this part calculates the pagerank for every iteration 
            # using the values fromt eh previous iterations
            # self.vectorUserMap[user][2] holds the current pagerank for 'user'
            # self.vectorUserMap[user][1] holds the previous pagerank for 'user'
            error = 0
            for user in self.vectorUserMap:
                    self.vectorUserMap[user][2] = (self.vectorUserMap[user][2] * self.alpha) + (1 - self.alpha) / N
                    error = max(error , abs(self.vectorUserMap[user][2] - self.vectorUserMap[user][1]))
            
           
            # we update the pageranks of all the users
            for user in self.vectorUserMap:
                self.vectorUserMap[user][1] = self.vectorUserMap[user][2] 
                self.vectorUserMap[user][2] = 0
            
            # exit the computation if the maximum error is minimized
            if(error < self.maxerror):
                #print error
                break
            
        self.normalizePageRanks()
        
    
    #ranks users on the basis of pagerank        
    def rankAllUsers(self):
        self.rankedUsers = sorted(self.vectorUserMap.items(), key=lambda(k, v):(v[1], k), reverse=True)
        
    def getTopKUsers(self, K):
        return self.rankedUsers[:K]    
    
    # here we take the union of all the users who were mentioned by someone
    # and the users who mentioned someone (except just themselves)
    def pruneUserMentionMap(self):
        mentionerOrMentioneeSet = self.setMentionees.union(self.setMentioners)
        self.setUsers = mentionerOrMentioneeSet
                
    def processUsers(self):
        listSortedUsers = sorted(list(self.setUsers))
        index = 0
        initialPageRank = 1.0 / float(len(listSortedUsers))
        for user in listSortedUsers:
            # we initialize all users with the initial value of page rank
            self.vectorUserMap[user] = [index, initialPageRank, 0]
            index = index + 1
  
    def populateUserMentionMap(self, tweet):
        userInfo = tweet['user']
        userName = userInfo['screen_name']
        entities = tweet['entities']
        mentions = entities['user_mentions']
        
        if(len(mentions) > 0):
            if not(len(mentions) == 1 and userName in mentions):
                # We consider all users as mentioners who mention 
                # atleast one user except themselves
                self.setMentioners.add(userName)
        if(userName not in self.usersMentionsMap) :    
            self.usersMentionsMap[userName] = []
        
        for mention in mentions:
            # If a user mentions herself then we dont consider it
            if userName == mention['screen_name']:
                continue;
            self.usersMentionsMap[userName].append(mention['screen_name'])
            self.setMentionees.add(mention['screen_name']) 
    
    # parses tweet line by line and calls populateUserMentionMap()
    # for each tweet
    def parseJson(self, filename):
        with open(filename) as fileData:
            for tweet in fileData:
                json_dict = loads(tweet.lower())
                self.populateUserMentionMap(json_dict)


    #def getZipfianRanks(self, rankedUsersList, totalUsersList):
        # results = OrderedDict()
        # rank = 1
        # revise the actual pagerank score by zipfian score
        # for rankedUser in rankedUsersList: 
        #    results[rankedUser] = 1 / float(rank)
        #    rank += 1
        #    totalUsersList.remove(rankedUser)
        
        # for all the unranked users we given them the same zipfian rank score
        #for unrankedUser in totalUsersList:
        #    results[unrankedUser] = 1 / float(rank)
        #return results

    def getRankScoresForUsers(self, usersList):
        usersDict = {}
        minrankValue = 1
        sum = 0
        for user in usersList:
            if user in self.vectorUserMap:
                sum += self.vectorUserMap[user][1]
                minrankValue = min(minrankValue, self.vectorUserMap[user][1])
        
        for user in usersList:
            if user in self.vectorUserMap:
                usersDict[user] = self.vectorUserMap[user][1] / sum
        
        # we remove all the ranked users from the usersList
        for user in self.vectorUserMap :       
            if user in usersList:
                usersList.remove(user)
   
        # now we are left with unranked users in usersList
        # assigning the minimum rank to the users which were not ranked
        for user in usersList:
            usersDict[user] = minrankValue /(2 * sum)
            
        #results = self.getZipfianRanks(rankedUsersList, usersList)
        return usersDict
        
def main():
    jsonFilename = 'E:\Padhai\IR\Homework\HW2\mars_tweets_medium.json'  # argv[1]
    start = time()
    tweetRanker = TweetUserRanking(jsonFilename)
    print 'It took' , time() - start , 'seconds to ranks the users'
    print tweetRanker.getRankScoresForUsers(['badastronomer','nasa','marscuriosity','kjugjhd'])
    


if __name__ == '__main__':
    main()
    
    
    
