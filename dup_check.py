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


# database connection
cnx = mysql.connector.connect(user='Sanders', password='cjf0329ABC!',
                              host='3.16.217.8',
                              database='cord_19')
cursor=cnx.cursor(buffered=True)

cnx1 = mysql.connector.connect(user='Sanders', password='cjf0329ABC!',
                              host='3.16.217.8',
                              database='cord_19')
cursor1=cnx.cursor(buffered=True)

cnx2 = mysql.connector.connect(user='Sanders', password='cjf0329ABC!',
                              host='3.16.217.8',
                              database='cord_19')
cursor2=cnx2.cursor(buffered=True)

sql_cmd="SELECT title,count(*) FROM NIH_test_1 where p_type not LIKE '%Letter%' and p_type  not LIKE '%Editorial%' and p_type  not LIKE '%News%' and p_type not like '%Erratum%' group by title order by count(*) desc limit 1598"

cursor1.execute(sql_cmd)
myresult = cursor1.fetchall()
count=0
main_file_name="dup_file.txt"
file1 = open(main_file_name,"w",encoding='utf-8')
t1=0
t2=0
for item in myresult:
   title=item[0]
   total=item[1]

   if ('"' in title):
    sql_cmd1="SELECT a_id,title,p_date FROM NIH_test_1 where title='"+title+"' and p_type not LIKE '%Letter%' and p_type not LIKE '%Editorial%' and p_type  not LIKE '%News%' and p_type not like '%Erratum%' order by p_date desc,LENGTH(s_id) DESC" ### keep the latest one, discard the rest
 
   else:
    sql_cmd1='SELECT a_id,title,p_date FROM NIH_test_1 where title="'+title+'" and p_type not LIKE "%Letter%" and p_type not LIKE "%Editorial%" and p_type  not LIKE "%News%" and p_type not like "%Erratum%" order by p_date desc,LENGTH(s_id) DESC' ### keep the latest one, discard the rest
   #print(sql_cmd1)   
   cursor.execute(sql_cmd1)
   myresult1 = cursor.fetchall()
   start=0 ### skip first one, we only want to exclude the other
   for item1 in myresult1:
     a_id=item1[0]
     title=item1[1]
     if (start==0): ### skip first one (latest)
      start=1
     else: ### exclude the rest records
      sql = "INSERT INTO NIH_test_excl (title,a_id) VALUES (%s,%s)"
      val = (title,a_id)
      cursor2.execute(sql, val)
      cnx2.commit()
     L=str(a_id)+"\n" ### store all info for check later
     file1.writelines(L)
   file1.writelines("====\n")
   count+=1
   print(count,"Done")

   
file1.close() #to change file access modes
#close the database connection
cursor.close()
cursor1.close()
cnx.close()
cnx1.close()
cnx2.close()
cursor2.close()
