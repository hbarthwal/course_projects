'''
Created on Apr 3, 2013

@author: Himanshu Barthwal
'''

from bing import DocumentsGenerator

class Classification:
    _bingDocsGenerator = DocumentsGenerator('')
    
    
    def _getDocuments(self):
        print 'Getting Documents for CLassification'
      
        queryList = ['bing', 'amazon', 'twitter', 'yahoo', 'google'
                     'beyonce', 'bieber', 'television', 'movies', 'music'
                     'obama', 'america', 'congress', 'senate', 'lawmakers']
        return self._bingDocsGenerator.getDocuments(queryList)