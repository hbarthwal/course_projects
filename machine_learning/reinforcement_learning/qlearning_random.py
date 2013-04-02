'''
Created on Mar 21, 2013

@author: Himanshu Barthwal
'''
from random import randint
from operator import itemgetter
from jinja2.runtime import to_string

class State:
    isGoalState = False
    name = ''
    rowIndex = 0
    columnIndex = 0
    actionRewardDict = {}
    qValuesDict = {}
    def __init__(self, name, rowIndex, columnIndex, actionRewardDict, isGoalState = False):
        self.rowIndex = rowIndex
        self.columnIndex = columnIndex 
        self.name = name
        self.isGoalState = isGoalState
        self.actionRewardDict = actionRewardDict
        self._initializeQValues()
    
    def _initializeQValues(self):
        self.qValuesDict = {}
        for action in self.actionRewardDict:
            self.qValuesDict[action] = 0
    
    def getMaxQValue(self):
        sortedValues = sorted(self.qValuesDict.items(), None , itemgetter(1) , True)
        return sortedValues[0][1]
        
    def getRewardForAction(self, action):
        if action in self.actionRewardDict:
            return self.actionRewardDict[action]
    
    def updateQValue(self, action, value):
        self.qValuesDict[action] = value
    
    def getRandomAction(self):
        numActions = len(self.actionRewardDict)
        randomIndex = randint(0, numActions - 1)
        action = self.actionRewardDict.keys()[randomIndex]
        return action
    
    def getReward(self, action):
        return self.actionRewardDict[action]
    
    def getSumOfQValues(self):
        tempsum = 0
        for action in self.qValuesDict:
            tempsum  = tempsum + self.qValuesDict[action]
        return tempsum

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
        #print '--------Iteration : ' + to_string(i) + '----------------'
        self.currentState = self._getRandomState()
        #print 'Chose initial state  ' , self.currentState.name     
        while not self.currentState.isGoalState:
                previousState = self.currentState
                action = self.currentState.getRandomAction()
                #print 'Chose action ', action 
                self._executeAction(action)
                #print 'Now currentstate is ', self.currentState.name
                             
                if not previousState is None:
                    #print 'Previous state is ', previousState.name
                    cumulativeReward = 0
                    if self.currentState.isGoalState:
                        cumulativeReward = previousState.getReward(action)
                    else:    
                        cumulativeReward = previousState.getReward(action) + self.gamma * self.currentState.getMaxQValue()
                    #print 'cumulativeReward for (', previousState.name,',',action ,') is ',cumulativeReward 
                    previousState.updateQValue(action, cumulativeReward)
    
    def performIterations(self):
        iterationCount = 0
        diffZeroCount = 0
        isDiffZero = False 
        while diffZeroCount <= self.maxDiffZeroCount:
            iterationCount += 1               
            self.performIteration()                
            self._updateSumOfQvalues()
            self._displayGrid(iterationCount)
            isDiffZero = abs(self.currentQValuesSum - self.previousQValuesSum) == 0
            if isDiffZero:
                diffZeroCount += 1
            else:
                diffZeroCount = 0
        print diffZeroCount,' is the diffZeroCount'
               
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
        print 'CurrentQSum = ', self.currentQValuesSum
        print 'PreviousQsum = ', self.previousQValuesSum
        print 'abs(sum Qt - sum Qt+1) = ', abs(self.currentQValuesSum - self.previousQValuesSum)


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
