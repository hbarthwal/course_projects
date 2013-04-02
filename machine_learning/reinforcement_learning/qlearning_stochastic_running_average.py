'''
Created on Mar 21, 2013

@author: Himanshu Barthwal
'''
from random import randint
from operator import itemgetter

class State:
    isGoalState = False
    name = ''
    rowIndex = 0
    columnIndex = 0
    actionRewardDict = {}
    qValuesDict = {}
    visitsDict = {}
    goalVisitDict = {}
    intendedActionProbability = 0.76
    unintendedActionProbability = 0.0
    estimatedRewardDict = {}
    intendedAction = ''
    
    def __init__(self, name, rowIndex, columnIndex, actionRewardDict, isGoalState = False):
        self.rowIndex = rowIndex
        self.columnIndex = columnIndex 
        self.name = name
        self.isGoalState = isGoalState
        self.actionRewardDict = actionRewardDict
        self._initializeQValues()
        self._initializeRewardDict()
        self._updateUnintendedProbabilitiy()
        self._initializeVisitsDict()
        self._initializeGoalVisitsDict()
    
    def _initializeQValues(self):
        self.qValuesDict = {}
        for action in self.actionRewardDict:
            self.qValuesDict[action] = 0
            
    def _initializeGoalVisitsDict(self):
        self.goalVisitDict = {}
        for action in self.actionRewardDict:
            self.goalVisitDict[action] = 0
    
    def _initializeVisitsDict(self):
        self.visitsDict = {}
        for action in self.actionRewardDict:
            self.visitsDict[action] = 0
    
    def _initializeRewardDict(self):
        self.estimatedRewardDict = {}
        for action in self.actionRewardDict:
            self.estimatedRewardDict[action] = 0
            
    def _updateUnintendedProbabilitiy(self):
        numUnintendedActions = len(self.actionRewardDict) - 1
        self.unintendedActionProbability = (1 - self.intendedActionProbability) / float(numUnintendedActions)
    
    def getMaxQValue(self):
        sortedValues = sorted(self.qValuesDict.items(), None , itemgetter(1) , True)
        return sortedValues[0][1]
        
    def getRewardForAction(self, action):
        if action in self.actionRewardDict:
            return self.actionRewardDict[action]
    
    def updateQValue(self, action, value):
        #print 'Qvalue for ', self.name, ',',action,'=',value 
        self.qValuesDict[action] = value
    
    def getQValue(self, action):
        return self.qValuesDict[action]
    
    def getStochasticAction(self):
        numActions = len(self.actionRewardDict)
        randomIndex = randint(0, numActions - 1)
        self.intendedAction = self.actionRewardDict.keys()[randomIndex]
        randomNum = .01 * randint(1, 100)
        
        if randomNum < self.intendedActionProbability:
            return self.intendedAction
        
        unintendedActionList = []
        for action in self.actionRewardDict:
            if action != self.intendedAction:
                unintendedActionList.append(action)
        
        numActions = len(unintendedActionList)
        randomIndex = randint(0, numActions - 1)
        stochasticAction = unintendedActionList[randomIndex]
        return stochasticAction
                
    def getReward(self, action):
        return self.actionRewardDict[action]
    
    def getSumOfQValues(self):
        tempsum = 0
        for action in self.qValuesDict:
            tempsum  = tempsum + self.qValuesDict[action]
        return tempsum
    
    def incrementVisit(self, action):
        if self.name == 'S3' or self.name == 'S5' or self.name == 'S9': 
            self.visitsDict[action] += 1
    
    def incrementGoalVisit(self, action):
        if self.name == 'S3' or self.name == 'S5' or self.name == 'S9': 
            self.goalVisitDict[action] += 1
    
    def getVisit(self, action):
        return self.visitsDict[action]
    
    def calculateExpectedReward(self):
        for action in self.actionRewardDict:
            if (self.name == 'S3' or self.name == 'S5' or self.name == 'S9') and self.visitsDict[action] != 0:
                print 'E[r(', self.name,',',action,')] = ', self.goalVisitDict[action] / float(self.visitsDict[action])  

class Grid:
    states = None 
    currentState = None
    actionTypeList = ['left', 'right', 'up', 'down']
    maxRowIndex = 0
    maxColIndex = 0
    gamma = 0.9
    currentQValuesSum = 0
    previousQValuesSum = 0
    maxDiffZeroCount = 10
    
    
    def __init__(self, states):
        self.states = states
        self.maxColIndex = len(self.states) - 1
        self.maxRowIndex = len(self.states[0]) - 1
        self.currentQValuesSum = 2
        self.previousQValuesSum = 1
       
    
    def _getRandomState(self):
        randomRowIndex = randint(0, self.maxRowIndex)
        randomColumnIndex = randint(0 , self.maxColIndex)
        state = self.states[randomRowIndex][randomColumnIndex]
        return state
       
    def _executeAction(self, actionType):
        if actionType == 'left':
            self.currentState = self.states[self.currentState.rowIndex][self.currentState.columnIndex - 1]
        if actionType == 'right':
            self.currentState = self.states[self.currentState.rowIndex][self.currentState.columnIndex + 1]
        if actionType == 'up':
            self.currentState = self.states[self.currentState.rowIndex - 1][self.currentState.columnIndex]
        if actionType == 'down':
            self.currentState = self.states[self.currentState.rowIndex + 1][self.currentState.columnIndex]
    
    def performIteration(self):
        self.currentState = self._getRandomState()
        while not self.currentState.isGoalState:
                selectedAction = self.currentState.getStochasticAction()
                previousState = self.currentState
                self._executeAction(selectedAction)
                previousState.incrementVisit(previousState.intendedAction)
                cumulativeReward = 0
                if self.currentState.isGoalState:
                    previousState.incrementGoalVisit(previousState.intendedAction)
                    cumulativeReward = previousState.getReward(selectedAction)
                else:    
                    cumulativeReward = previousState.getReward(selectedAction) + self.gamma * self.currentState.getMaxQValue()
                
                alpha = 1 / float(1 + previousState.getVisit(previousState.intendedAction))
                qvalue = (1 - alpha) * previousState.getQValue(previousState.intendedAction) + alpha * cumulativeReward
                previousState.updateQValue(previousState.intendedAction, qvalue)
                    
    
    def performIterations(self):
        iterationCount = 0
        diffZeroCount = 0
        isDiffZero = False 
        while diffZeroCount <= self.maxDiffZeroCount:
            iterationCount += 1               
            self.performIteration()                
            self._updateSumOfQvalues()
            self._displayGrid(iterationCount)
            print '----------------------------'
            isDiffZero = abs(self.currentQValuesSum - self.previousQValuesSum) < 0.01
            if isDiffZero:
                diffZeroCount += 1
            else:
                diffZeroCount = 0
               
    def _updateSumOfQvalues(self):
        self.previousQValuesSum = self.currentQValuesSum
        self.currentQValuesSum = 0
        for stateList in self.states:
            for state in stateList:
                self.currentQValuesSum += state.getSumOfQValues()
    
    def _displayGrid(self, iterNum):
        print '---------Iteration : ', iterNum ,'--------------'
        for i in range(3):
            for state in self.states[i]:
                print state.name, ' --> ',state.qValuesDict
                state.calculateExpectedReward()
        print 'abs(sum (Qt) - sum (Qt+1)) = ', abs(self.currentQValuesSum - self.previousQValuesSum)



def main():
    print 'Main'
    S1 = State('S1', 0, 0, {'right': 0,'down': 0})
    S2 = State('S2', 0, 1, {'right': 0,'down': 0,'left': 0})
    S3 = State('S3', 0, 2, {'down': 100,'left': 0})
    S4 = State('S4', 1, 0, {'right': 0,'down': 0,'up': 0})
    S5 = State('S5', 1, 1, {'right': 100,'down': 0,'left': 0,'up': 0})
    S6 = State('S6', 1, 2, {}, True)
    S7 = State('S7', 2, 0, {'right': 0,'up': 0})   
    S8 = State('S8', 2, 1, {'right': 0,'left': 0,'up': 0})   
    S9 = State('S9', 2, 2, {'left': 0,'up': 100}) 
    states = list() 
    states.append([S1,S2,S3])
    states.append([S4,S5,S6])
    states.append([S7,S8,S9])
    
    statesGrid = Grid(states)
    statesGrid.performIterations()
    
if __name__ == "__main__":
    main()    
