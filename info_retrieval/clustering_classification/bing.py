'''
Created on Apr 2, 2013

@author: Himanshu Barthwal

'''
from urllib import quote
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler
from urllib2 import build_opener, urlopen, install_opener
from json import loads, dumps
from pprint import pprint
from os.path import exists
from os import remove

class DocumentsGenerator:
    _username = 'shady.barthu@gmail.com'
    _accountKey = 'Gl9MAPhfLPhqU7GCHykh/8QW0f3yZlVu5r0vZM3YRfU='
    _cacheFile = ''
    
    def __init__(self, cacheFile):
        self._cacheFile = cacheFile
    
    def _getDocumentsFromBing(self, bingQuery, skip, category = ''):
        query = quote("'" + bingQuery + "'")
        if category != '':
            category = quote("'" + 'rt_' + category.strip() + "'")
            category = '&NewsCategory='  + category
    
        rootURL = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/"
        searchURL = rootURL + "News?Query=" + query + "&$format=json" + category 
        
        if skip > 0:
            searchURL = searchURL + "&$skip=%d" % (skip)
    
        print searchURL
        passwordManager = HTTPPasswordMgrWithDefaultRealm()
        passwordManager.add_password(None, searchURL, self._username, self._accountKey)
    
        handler = HTTPBasicAuthHandler(passwordManager)
        opener = build_opener(handler)
        install_opener(opener)
        readURL = urlopen(searchURL).read().lower()
        
        data = loads(readURL)
        documents = data['d']['results']
        return documents
    
    def _cacheDocuments(self, documents):
        print '-----------Downloading documents to local file system'
        with open(self._cacheFile, 'a') as file:
            file.write(dumps(documents))
       
    def _getCachedDocs(self):
        print 'Returning docs from cache'
        with open(self._cacheFile, 'r') as file:
            return loads(file.read())
        
    def _areDocsCached(self):
        return exists(self._cacheFile)
    
    def getDocuments(self, queryList, categories = [], numResults = 30):
        documents = []
        hasCategory = len(categories) > 0
        try:
            if self._areDocsCached():
                return self._getCachedDocs()
            
            if not hasCategory:
                categories = ['']
                
            for category in categories:
                documentsBatch2 = None
                for query in queryList:
                    documentsBatch1 = self._getDocumentsFromBing(query, 0, category)
                    resultCount = 0
                    for document in documentsBatch1:
                        if resultCount == numResults:
                            print 'break'
                        document['query'] = query
                        if hasCategory:
                            document['category'] = category
                        documents.append(document)
                        resultCount += 1
                        
                    if numResults > 15:
                        documentsBatch2 = self._getDocumentsFromBing(query, numResults / 2, category)
                        for document in documentsBatch2:
                            if resultCount == numResults:
                                print 'break'
                            document['query'] = query
                            if hasCategory:
                                document['category'] = category
                            documents.append(document)
                            resultCount += 1
                            
            self._cacheDocuments(documents)
        
        except:
            if exists(self._cacheFile):
                remove(self._cacheFile)
            raise
        print 'Returning documents'
        return documents

def main():
    print 'Main'
    documentsGenerator = DocumentsGenerator('/tmp/a.dat')
    pprint (documentsGenerator.getDocuments(['texas aggie', 'aggie longhorn']))
    
if __name__ == "__main__":
    main()  