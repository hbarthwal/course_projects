'''
Created on Apr 2, 2013

@author: Himanshu Barthwal

'''
from urllib import quote
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
from urllib2 import build_opener, urlopen, install_opener
from json import loads
from pprint import pprint
from os.path import exists

class DocumentsGenerator:
    _username = 'shady.barthu@gmail.com'
    _accountKey = 'Gl9MAPhfLPhqU7GCHykh/8QW0f3yZlVu5r0vZM3YRfU='
    _cacheFile = ''
    
    def __init__(self, cacheFile):
        self._cacheFile = cacheFile
    
      
    def _getDocumentsFromBing(self, bingQuery, skip, category):
        query = quote("'" + bingQuery + "'")
    
        rootURL = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/"
        searchURL = rootURL + "News?Query=" + query + "&$format=json" + category 
        
        if skip > 0:
            searchURL = searchURL + "&$skip=%d" % (skip)
    
        passwordManager = HTTPPasswordMgrWithDefaultRealm()
        passwordManager.add_password(None, searchURL, self.username, self.accountKey)
    
        handler = HTTPBasicAuthHandler(passwordManager)
        opener = build_opener(handler)
        install_opener(opener)
        readURL = urlopen(searchURL).read()
        
        data = loads(readURL)
        documents = data['d']['results']
        return documents
    
    def _cacheDocuments(self, documents):
        print 'Downloading documents to local file system'
        with open(self._cacheFile, 'w') as file:
            file.write(documents)
       
    def _getCachedDocs(self):
        print 'Returning docs from cache'
        with open(self._cacheFile, 'w') as file:
            return loads(file.read())
        
    def _areDocsCached(self):
        return exists(self._cacheFile)
    
    def getDocuments(self, queryList):
        if self._areDocsCached():
            print 'Got docs' #return self._getCachedDocs()
        documents = []
        for query in queryList:
            documentsBatch1 = self._getDocumentsFromBing(query, 0)
            documentsBatch2 = self._getDocumentsFromBing(query, 15)
            documents.append(document for document in documentsBatch1)
            documents.append(document for document in documentsBatch2)
        
        self._cacheDocuments(documents)
        return documents
    

def main():
    print 'Main'
    documentsGenerator = DocumentsGenerator()
    result1 = documentsGenerator.getDocuments(['texas', 'aggies'], 0)
    print 'Got ', len(result1), ' results'                           
    pprint(result1)
    
    result2 = documentsGenerator.getDocuments(['texas', 'aggies'], 16)
    print 'Got ', len(result2), ' results'                           
    pprint(result2)
    
if __name__ == "__main__":
    main()  