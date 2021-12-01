
import requests
import json,ast
from json import loads
from collections import OrderedDict
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import xlsxwriter
from .database_query import DatabaseQuery


sql_query = DatabaseQuery ()

### for UC 6+2 login
def uc_authenticate(username, password):
    '''
    If authentication is successful, returns a user dict containing username, email, first_name, last_name.
    If authentication fails, returns None.
    '''
    UCAD_API_URL = 'https://chi-tools.uc.edu/auth/api/authenticate'
    UCAD_API_ACCESS_TOKEN = '8vREeGcakA9ASr9u'
    payload = {
        'username' : username,
        'systems' : 'ucad',
    }
    headers = {
       'x-password' :  password,
       'x-access-token' : UCAD_API_ACCESS_TOKEN,
    }
    r = requests.get(UCAD_API_URL, params=payload, headers=headers)
    response = r.json()
    if response['authenticated']:
        username=response['user']['username']
        #email=response['user']['email']
        first_name=response['user']['first_name']
        #last_name=response['user']['last_name']
        return first_name
    else:
        return "Not found"

### used to clean html tags
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def get_task_list(account_id):
    # get the latest repository
    #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    #cursor.execute('SELECT task,q_aid,aid_relevance,qstr FROM cord_19.flask_selections2 where uid= %s order by save_date desc', (session['id'],))
    # Fetch all tasks for a particular user
    task_list={}
    
    #tasks = cursor.fetchall()
    tasks = sql_query.find_task (account_id = account_id, order_by = 'save_date', ascending = False)
    
    for item in tasks:
         task_id=item['task']
         if (item['q_aid']=='999998'):
            search_id=item['qstr'] ### for query
         else:
            search_id=item['q_aid'] ### for pmid or a_id

         task_list[task_id]=search_id
 
    #cursor.close()
    return task_list

def load_search_result (account_id, path,stage,a_id, sql_query): ### read json files and pass to templates for display
    if (stage=="other"):
            files = {}
            email=""
            if (a_id=='999998'): ### query str
             json_file_name = account_id +"_"+str(a_id)+".json"
            else:
             json_file_name=str(a_id)+".json"
            print("We will read: ",json_file_name)
            with open(path+"/"+json_file_name) as json_file:
                                   data1 = json.load(json_file,object_pairs_hook=OrderedDict)
                                   data = ast.literal_eval(json.dumps(data1))
                                   email=""
                                   count=0
                                   
                                   if (a_id=='999998'):
                                      total_return=data['summary'][0]['total_return']
                                   else:
                                      total_return=30 ### for doc-based match
 
                                   mydict={}
                                   for p in data['abstract']:
                                    name=p['abstract_id']
                                    title=""
                                    abs=""
                                    first_para=""
                                    doi=""
                                    has_full_text=""
                                    authors=""
                                    journal=""
                                    publish_time=""
                                    pubmed_id=0
                                    source_x=""
                                    score=0
                                    p_type=""
                                    ori_abs=None
                                    citation_count=0
                                    title=title.join(p['title'])
                                    abs=abs.join(p['abstract'])
                                    #abs=abs.encode('ascii').decode('unicode_escape') 
                                
                                    if ("Key Sentences" in abs):
                                     key_sentences=abs.split("Key Sentences:")[1]
                                     ori_abs=abs.split("Key Sentences:")[0].strip()
                                     key_sentences_list=key_sentences.split("<br>")
                                     sentences=nltk.sent_tokenize(ori_abs)

                                    if (a_id=='999998'): ###tmp 
                                     first_para=first_para.join(p['first_para'])
                                     #first_para=first_para.encode('ascii').decode('unicode_escape')
                                    else: ### produce top 3 sentences for doc-based match
                                     if ("Key Sentences" in abs): 
                                      s_count=0
                                      for s in sentences:
                                       s=s.strip()
                                       if (s_count<3):
                                         s=cleanhtml(s)
                                         first_para+=s
                                         s_count+=1
                                      abs=cleanhtml(ori_abs)
                                      #for ks in key_sentences_list:
                                          #ks=cleanhtml(ks)
                                          #new_ks="<font color='red'>"+ks+"</font>"
                                          #new_abs=abs.replace(ks,new_ks)
                                      #abs=new_ks 
                                     else:
                                      abs=ori_abs
 
                                    doi=doi.join(p['doi'])
                                    score=float(p['score']) ###str to float
                                    authors=authors.join(p['authors'])
                                    #authors=authors.encode('ascii').decode('unicode_escape')
                                    pubmed_id=str(p['pubmed_id'])
                                    if (a_id=='999998'): ###tmp
                                     citation_count=p['citation_count']
                                    
                                    if (pubmed_id!=''):
                                       
                                       ori_pmid=pubmed_id
                                       pubmed_id="(PMID: "+pubmed_id+")"
                                       
                                       #sql_cmd="SELECT citation_count FROM cord_19.citation_summary where pmid="+ori_pmid
                                       #cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                                       #cursor1.execute(sql_cmd)
                                       #myresult = cursor1.fetchone()
                                       query_result = sql_query.find_citation_count (ori_pmid)
                                       if (query_result):
                                           citation_count = query_result['citation_count']

                                       #cursor1.close()
                                    source_x=source_x.join(p['source_x'])

                                    p_type=str(p['p_type'])

                                    p_time=publish_time.join(p['publish_time'])
                                    publish_time=p_time[0:10]
                                    journal=journal.join(p['journal'])
                                    if (len(journal)==0):
                                      journal=source_x
                                     
                                    meta="Authors: "+authors+"<br>"+"Journal/Source: "+journal+" "+pubmed_id+" <br>"+"Publish time: "+publish_time
                                    mydict[name]={"title":title,"score":score,"meta":meta,"abs":abs,"doi":doi,"p_type":p_type,"first_para":first_para,"citation_count":citation_count}


            return mydict, total_return



def generate_annotation_summary (account_id):
     wb = xlsxwriter.Workbook('/var/www/flask/covid_iqs/static/process/annotation.xlsx')
     tasks = sql_query.find_task (account_id = account_id, aid_relevance_not_null = True, order_by = 'task')


     for item in tasks:
         rid_list=[]
         rel_list=[]
         pmid_list=[]
         task_id=item['task']
         task_alias=item['task_alias']
         if(task_alias):
          task_name=task_alias+" (id-"+str(task_id)+")"
         else:
          task_name="None"+" (id-"+str(task_id)+")"

         #task_name='Task '+str(task_id)
         ws=wb.add_worksheet(task_name)
         x_pos=1
         y_pos=0
         ws.write(0,0,'Article ID')
         ws.write(0,1,'PubMed ID')
         ws.write(0,2,'Relevance')

         q_aid=item['q_aid']
         qstr=item['qstr']
         relevance=item['aid_relevance']
         id_list=relevance.split("||")
         for id in id_list:
             rel=str(id).split("_")
             if (len(rel)==2):
              sid=int(rel[0])
              result = sql_query.find_specific_article (sid, 'a_id')
              if result:
               pubmed_id=str(result['pmid'])
              else:
               pubmed_id=''
              relevance=rel[1]
              ws.write(x_pos,y_pos,sid)
              ws.write(x_pos,y_pos+1,pubmed_id)
              ws.write(x_pos,y_pos+2,relevance)
              x_pos+=1

     #the writer has done its job
     wb.close()