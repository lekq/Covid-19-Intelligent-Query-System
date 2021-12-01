# -*- coding: utf-8 -*-
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import codecs
import sys
import xml.etree.ElementTree as ET
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import mysql.connector
from mysql.connector import errorcode
import sys
import argparse
batch_size=130
import time
from elasticsearch import Elasticsearch
import logging
import json
import os
import glob
from nltk.corpus import stopwords
import spacy
import pytextrank
import re
from text2digits import text2digits
t2d = text2digits.Text2Digits()
from nltk.tokenize import word_tokenize
import string
import nltk
import os.path
from os import path
from dateutil.parser import parse

data={}
data['abstract']=[]

user_name=sys.argv[1]
term_list=sys.argv[2]
aid=sys.argv[3]
new_q=sys.argv[4]
eid_list=sys.argv[5]
id_list=eid_list.split(",")
print ("id list",id_list)

# load a spaCy model, depending on language, scale, etc.
nlp = spacy.load("en_core_web_sm")

# add PyTextRank to the spaCy pipeline
tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}], http_auth=('elastic', 'j3LsO9VKhT0IjPyNxuzI'))
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es

es=connect_elasticsearch()                      

limit=30
# query to get match PMIDs
def get_PMIDs(exp_query):
    if es is not None:
     res_list= es.search(index='nih_1',body={
     "min_score":2,
     "query": {
      "multi_match": {
      "query": exp_query,
      "type": "best_fields", 
      "fields": ["title","abstract","meta_terms"],
      "tie_breaker": 0.3

     }
    }

    },size=limit)
    return res_list 


if (term_list):
 query=term_list

print("Query term list:", query)
c_count=0


res=get_PMIDs(query)
for info in res['hits']['hits']:
  if (c_count<=limit):
          a_id=info['_source']['a_id']
          p_type=info['_source']['p_type']
          if (str(a_id) in id_list):
           print ("Remove from the result:",a_id)
          else:
           c_count+=1 
           score=info['_score']
           title=info['_source']['title']
           abstract=info['_source']['abstract']
           print("score:",score)
           title_utf8=title.encode('UTF-8')
           abstract_utf8=abstract.encode('UTF-8')

           sum_abs="None"
           c_str=""
           if (len(abstract_utf8)>5):  
             sum_abs="<font color='blue'>Key Sentences:</font><br>"
             t_file="/var/www/flask/covid_iqs/static/process/textrank/"+str(a_id)+".txt"
             if (os.path.isfile(t_file)):
              f=open(t_file, "r",encoding='utf-8')
              for line in f:
                 line=line.strip()
                 c_str+="<font color='green'>"+line+"</font><br><br>"
             else:
              doc = nlp(str(abstract))
              for sent in doc._.textrank.summary(limit_phrases=20, limit_sentences=8):
               key_sent=str(sent).strip()
               c_str+="<font color='green'>"+key_sent+"</font><br><br>"
             sum_abs+=c_str

           abstract+="<br><br>"+sum_abs
           
           condition=info['_source']['symp']
           cd=info['_source']['cd'] 
           target=info['_source']['target'] 
           device=info['_source']['device']

           doi=info['_source']['doi']
           publish_time=info['_source']['p_date']
           authors=info['_source']['authors']
          
           journal=info['_source']['journal']
           pubmed_id=info['_source']['pmid'] 
           source_x=info['_source']['source']

           data['abstract'].append({
             'abstract_id': a_id,
             'title': title,
             'abstract': abstract,
             'doi':doi,
             'publish_time':publish_time,
             'authors':authors,
             'journal':journal,
             'source_x':source_x,
             'pubmed_id':pubmed_id,
             'score':score,
             'p_type':p_type,
             'condition':condition,
             'cd':cd,
             'target':target,
             'device':device
           })
           print (a_id)


json_file_name="/var/www/flask/covid_iqs/test/"+str(aid)+".json"
print(json_file_name)

if (new_q=='yes' and path.exists(json_file_name)): #New query-> Delete original query
 print ("Remove: ",json_file_name)
 os.remove (json_file_name) ### remove after update the whole db

with open(json_file_name, 'w') as outfile:
  json.dump(data, outfile)

