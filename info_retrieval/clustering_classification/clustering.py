'''
Created on Apr 3, 2013

@author: Himanshu Barthwal
'''
from bing import DocumentsGenerator

class Clustering:
    
    _bingDocsGenerator = DocumentsGenerator('')
    
    def _getDocuments(self):
        print 'Getting documents for clustering'
        queryList = ['texas aggies', 'texas longhorns',
                     'duke blue devils','dallas cowboys',
                     'dallas mavericks']
        
        return self._bingDocsGenerator.getDocuments(queryList)