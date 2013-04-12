'''
Created on Apr 8, 2013

@author: Himanshu Barthwal
'''
from bing import DocumentsGenerator
from vector_space import VectorSpace
from random import randint
from operator import itemgetter
from sys import argv

class KMeans:
    
    _bingDocsGenerator = None
    _vectorSpace = None
    _vectorsInfo = [{'vector':[], 'class':'texas aggies'}]
    _classList = ['texas aggies', 'texas longhorns',
                 'duke blue devils','dallas cowboys',
                 'dallas mavericks']
    _expectedNumberOfClusters = 50
    _clusters = {'cluster1' : {'vectorIndices':set(), 'center' : [], 
                               'assignedclasses':{'texas aggies': 0}
                            }
                }
    
    
    def __init__(self, dataCacheFilePath):
        self._bingDocsGenerator = DocumentsGenerator(dataCacheFilePath)
        self._vectorSpace = VectorSpace(self._populateDocuments(), True, True)
        self._vectorsInfo =  self._vectorSpace.getAllDocumentVectors()
    
    def _populateDocuments(self):
        print 'Getting documents for clustering'
        jsonData = self._bingDocsGenerator.getDocuments(self._classList)
        print len(jsonData), ' is the number of documents'
        return jsonData
    
    def _generateRandomPoint(self):
        numberOfPoints = len(self._vectorsInfo)
        randomIndex = randint(0, numberOfPoints - 1)
        randomPoint = self._vectorsInfo[randomIndex]
        return randomPoint
    
    def _getDistance(self, docVector1, docVector2):
        return self._vectorSpace.getEuclidianDistance(docVector1, docVector2)
        
    def _isContained(self, vectorList, vectorElement):
        for vector in vectorList:
            if self._vectorSpace._areEqual(vector['vector'], vectorElement['vector']):
                return True
        return False
        
    def _initializeClusters(self):
        print 'Initializing clusters'
        randomCenters = []
        while True:
            randomCenter = self._generateRandomPoint()
            
            if not self._isContained(randomCenters, randomCenter):
                randomCenters.append(randomCenter)
            
            if len(randomCenters) == self._expectedNumberOfClusters:
                break
        
        tempClusters = {}
        clusterIndex = 0
        for randomCenter in randomCenters:
            tempCluster = {'center' : randomCenter, 'vectorIndices' : set()}
            tempClusterName = 'cluster' + str(clusterIndex)
            clusterIndex += 1
            tempClusters[tempClusterName] = tempCluster
        self._clusters = tempClusters
        
    def _calculateRSS(self):
        distanceSum = 0
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            clusterCenter = cluster['center']['vector']
            for vectorIndex in cluster['vectorIndices']:
                distance = self._getDistance(clusterCenter, self._vectorsInfo[vectorIndex]['vector'])
                distanceSum += distance
        RSS = distanceSum / len(self._clusters)
        return RSS
    
    def _findClosestCluster(self, docVector):
        distanceList = []
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            clusterCenter = cluster['center']['vector']
            distance = self._getDistance(clusterCenter, docVector)
            distanceList.append((clusterName, distance))
        closestClusterName = min(distanceList, key=itemgetter(1))[0]
        return closestClusterName
     
    def _assignDocVectorToCluster(self, docVectorIndex, clusterName):
        cluster = self._clusters[clusterName]
        cluster['vectorIndices'].add(docVectorIndex)
        docVectorClass = self._vectorsInfo[docVectorIndex]['class']
        if not 'assignedclasses' in cluster:
            cluster['assignedclasses'] = {}
        assignedClasses = cluster['assignedclasses']
        if docVectorClass in assignedClasses:
            assignedClasses[docVectorClass] += 1
        else:
            assignedClasses[docVectorClass] = 1
      
    def _calculateCentroids(self):
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            vectors = []
            for vectorIndex in cluster['vectorIndices']:
                vectors.append(self._vectorsInfo[vectorIndex]['vector'])
            if len(vectors) > 0: 
                centroid = self._vectorSpace.getCentroid(vectors)
                cluster['center'] = {'vector': centroid}

    def _removeEmptyClusters(self):
        emptyClusterNames = []
        for clusterName in self._clusters:
            if len(self._clusters[clusterName]['vectorIndices']) == 0:
                emptyClusterNames.append(clusterName)
        for emptyClusterName in emptyClusterNames:
            self._clusters.pop(emptyClusterName)
            
    def _clearClusterMembers(self):
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            cluster['vectorIndices'].clear()
            cluster['assignedclasses'].clear()
    
    def clusterPoints(self):
        print 'Clustering Points'
        self._initializeClusters()
        iterCount = 0
        while True:
            vectorIndex = 0
            # Assign all vectors to clusters
            for vectorInfo in self._vectorsInfo:
                closestClusterName = self._findClosestCluster(vectorInfo['vector'])
                self._assignDocVectorToCluster(vectorIndex, closestClusterName)
                vectorIndex += 1
            print 'Iteration---'
            for clusterName in self._clusters:
                print clusterName ,'--->' ,self._clusters[clusterName]['assignedclasses']
            
            RI = self.getRandIndex()
            print 'RI : ', RI            
            RSS = self._calculateRSS()
            print 'RSS:', RSS
            purity = self.getPurity()
            print 'Purity is', purity

            if iterCount > 10:
                print 'Restarting !!----------------------------------------------------------------------'
                self._initializeClusters()
                iterCount = 0
                continue
            
            self._calculateCentroids()
            self._clearClusterMembers()
            iterCount += 1
            

    def _getVectorClassCounts(self):
        vectorCountDict = {}
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            vectorCountDict[clusterName] = {}
            for className in self._classList:
                vectorCountDict[clusterName][className] = 0
                for vectorIndex in cluster['vectorIndices']:
                    if self._vectorsInfo[vectorIndex]['class'] == className:
                        vectorCountDict[clusterName][className] += 1
        return vectorCountDict


    def getMaxCountClass(self, vectorCountDict, clusterName):
            maxCount = 0
            classCountDict = vectorCountDict[clusterName]
            for className in classCountDict:
                classCount = classCountDict[className]
                if classCount > maxCount:
                    maxCount = classCount
            return maxCount

  
    def _belongToSameCluster(self, vectorIndex1, vectorIndex2):
        for clusterName in self._clusters:
            cluster = self._clusters[clusterName]
            vectorIndices = cluster['vectorIndices']
            if  vectorIndex1 in vectorIndices and vectorIndex2 in vectorIndices:
                return True
        return False
        
    def getPurity(self):
        print 'Calculating purity'
        vectorCountDict = self._getVectorClassCounts()
        maxCountSum = 0
        for clusterName in vectorCountDict:
            maxCount = self.getMaxCountClass(vectorCountDict, clusterName)
            maxCountSum += maxCount
        purity = maxCountSum / float(len(self._vectorsInfo))
        return purity
    
    def getRandIndex(self):
        print 'Calculating Rand Index'
        falsePositivesCount = 0
        falseNegativesCount = 0
        truePositivesCount = 0
        trueNegativesCount = 0
        
        for vectorIndex1 in range(len(self._vectorsInfo)):
            for vectorIndex2 in range(len(self._vectorsInfo)):
                if vectorIndex1 == vectorIndex2:
                    continue
                else:
                    vectorInfo1 = self._vectorsInfo[vectorIndex1]
                    vectorInfo2 = self._vectorsInfo[vectorIndex2]
                    haveSameClass = vectorInfo1['class'] == vectorInfo2['class']
                    haveSameCluster = self._belongToSameCluster(vectorIndex1, vectorIndex2)

                    if haveSameClass:
                        if haveSameCluster:
                            truePositivesCount += 1
                        else :
                            falseNegativesCount += 1
                    else:
                        if haveSameCluster:
                            falsePositivesCount += 1
                        else :
                            trueNegativesCount += 1
        total = trueNegativesCount + truePositivesCount + falseNegativesCount + falsePositivesCount
        RI = float(truePositivesCount + trueNegativesCount) / total
        return RI

def main():
    print 'Main'
    #'/tmp/data.json'
    clustering = KMeans('kmeans.json')
    clustering.clusterPoints()
    

if __name__ == "__main__":
    main()  
    
    
    
        
        
    