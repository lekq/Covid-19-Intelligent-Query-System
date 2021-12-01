import xlrd
import os
import time
import fnmatch
import csv

import mysql.connector
from mysql.connector import errorcode

# Establish a MySQL connection

cnx = mysql.connector.connect(user='xxx', password='xxx',
                               host='xxx',
                               database='cord_19')
cursor=cnx.cursor(buffered=True)

processed_file='example.csv'

# Create the INSERT INTO sql query

# Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
count=0
# Open the workbook and define the worksheet
for file in os.listdir('./'):
    if fnmatch.fnmatch(file, processed_file):
     print (file)

     with open(file, 'r') as csvFile: 
      csv_data = csv.DictReader(csvFile)
      for row in csv_data:
       count+=1
       
       doi=row['DOI']
       version=row['Latest Version']
       authors=row['Authors']
       pmcid=row["PMCID"]
       pmid=row["PMID"]
       print(pmid)
       title=title=row['Title']
       pmcid=row['PMCID']
       abstract1=row['Abstract']
       abstract=abstract1
       source=row["Source"]
       a_count=row["Author Count"]
       journal=row['Journal Name Full']
       p_type=row['Publication Types']
       p_date=row['Publication Date']
       condition=row['Condition']
       print(condition)
       cd=row['Chemicals & Drugs']
       target=row['Target']
       device=row["Devices"]
       s_id=row["System ID"]
       total_citation=row["Total Citations"]
       ISSN=row["ISSN"]
       relevance=row["Relevance"]
       print("-------------")

       cursor.execute('INSERT INTO NIH_test1 (version,authors,s_id,doi,pmcid,pmid,p_date,p_type,source,title,abstract,symp,cd,target,device,a_count,journal,citation_count,ISSN,relevance)' 'VALUES(%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s)',(version,authors,s_id,doi,pmcid,pmid,p_date,p_type,source,title,abstract,condition,cd,target,device,a_count,journal,total_citation,ISSN,relevance))
       cnx.commit()
      

print ("Count:",count)
# Close the cursor
cursor.close()


# Close the database connection
cnx.close()

print ("All Done! Bye, for now.")
