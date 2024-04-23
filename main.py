import pandas
import requests as rq
import googleapiclient.discovery as discovery

url = "https://docs.google.com/document/d/11Cjs8vCk5shnmpmfTYfbWvJcqStDpsRZSt2iZ2z1h20/edit?usp=sharing"
id = "11Cjs8vCk5shnmpmfTYfbWvJcqStDpsRZSt2iZ2z1h20"

from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools

page = rq.get(url)

discovery_doc = "https://docs.googleapis.com/$discovery/rest?version=v1"

print(page.headers)

docs_service = discovery.build('docs', 'v1', rq, discoveryServiceUrl=discovery_doc)
doc = docs_service.documents().get(documentId=id).execute()
doc_content = doc.get('body').get('content')


#this might help https://developers.google.com/docs/api/samples/extract-text#python
