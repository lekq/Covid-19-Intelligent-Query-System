# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import sys
import os.path
from os import path
import json,ast
from json import loads
from collections import OrderedDict
from operator import getitem
import demjson
import operator
from operator import itemgetter

import mysql.connector
import spacy
import pytextrank
from nltk.tokenize import word_tokenize
import string
from nltk.corpus import stopwords
import subprocess

def nlp_processing(text):
  tokens = word_tokenize(text)
  # convert to lower case
  tokens = [w.lower() for w in tokens]
  # remove punctuation from each word
  table = str.maketrans('', '', string.punctuation)
  stripped = [w.translate(table) for w in tokens]
  # remove remaining tokens that are not alphabetic
  words = [word for word in stripped if word.isalpha()]
  # filter out stop words
  stop_words = set(stopwords.words('english'))
  words = [w for w in words if not w in stop_words]
  return words


mydb = mysql.connector.connect(
  host="localhost",
  user="dummy",
  password="123456",
  database="cord_19"
)

mycursor = mydb.cursor()


### for term search
sql_cmd="select a_id, title, abstract from NIH_test_1 where p_type not LIKE '%Letter%' and p_type  not LIKE '%Editorial%' and p_type  not LIKE '%News%' and p_type not like '%Erratum%' and a_id > {} order by a_id asc"

mycursor.execute(sql_cmd.format(0))

new_q='yes'
new_eid_list=''

while True:
  try:
    row = mycursor.fetchone()
  except Exception as e:
    print(e)
    mydb = mysql.connector.connect(
      host="localhost",
      user="dummy",
      password="123456",
      database="cord_19"
    )
    mycursor = mydb.cursor()
    mycursor.execute(sql_cmd.format(last_a_id))
    row = mycursor.fetchone()
  if row is None:
    break
  a_id, title, abstract = row
  a_id = str(a_id)
  last_a_id = a_id
  query_content=str(title)+". "+str(abstract)
  query_content=str(query_content.encode('utf-8'))
  term_list=nlp_processing(query_content)
  query_terms=""

  for term in term_list:
   query_terms+=' +"'+term+'"'

  print(a_id)
  print(query_terms)
  
  json_file_name="/var/www/flask/covid_iqs/test/"+str(a_id)+".json" ### create your own direction for json files
  if (path.exists(json_file_name)):
     print ("File is available:",json_file_name)
  else:
     cmd="python3 /var/www/flask/covid_iqs/es.py Sander "+'"'+query_terms+'" '+a_id+" '"+new_q+"' '"+new_eid_list+"'"
     print(cmd)
     os.system(cmd)
  print("------------------")

mycursor.close()
mydb.close()
