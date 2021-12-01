# -*- coding: utf-8 -*-
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sys
import json
import mysql.connector
from mysql.connector import errorcode
import sys
import argparse
batch_size=130
import time
import logging
import json
import os
import glob
from nltk.corpus import stopwords
import spacy
import pytextrank
import re
from nltk.tokenize import word_tokenize
import string
import nltk


# load a spaCy model, depending on language, scale, etc.
nlp = spacy.load("en_core_web_sm")

# add PyTextRank to the spaCy pipeline
tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)

# database connection
cnx = mysql.connector.connect(user='Sanders', password='cjf0329ABC!',
                              host='3.16.217.8',
                              database='cord_19')
cursor=cnx.cursor(buffered=True)

cnx1 = mysql.connector.connect(user='Sanders', password='cjf0329ABC!',
                              host='3.16.217.8',
                              database='cord_19')
cursor1=cnx.cursor(buffered=True)

sql_cmd="select a_id,abstract from NIH_test_1 where (abstract !='' and abstract is not NULL and abstract !='null') order by a_id asc"
cursor1.execute(sql_cmd)
myresult = cursor1.fetchall()
c_str=""
for item in myresult:
   c_str=""
   a_id=item[0]
   abstract=item[1]
   if (len(abstract)>5): 
      main_file_name="/var/www/flask/iqs/static/process/textrank/"+str(a_id)+".txt"
      print(main_file_name)
      try:
       doc = nlp(str(abstract))
       for sent in doc._.textrank.summary(limit_phrases=20, limit_sentences=8):
              key_sent=str(sent).strip()
              if(len(key_sent.split())>=5): #at least 5 words in a sent
                 c_str+=key_sent+"\n"
      except:
       print("***Skip a_id: ",main_file_name)
  
      file1 = open(main_file_name,"w",encoding='utf-8')
      file1.writelines(c_str)
      file1.close() #to change file access modes
          

#close the database connection
cursor.close()
cursor1.close()
cnx.close()
cnx1.close()
