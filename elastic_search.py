from elasticsearch import Elasticsearch
import nltk
from nltk.tokenize import word_tokenize
import spacy
from .utility import sql_query
import pytextrank
import os
import os.path
from os import path
import json

class ElasticSearchIQS:
    def __init__ (self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}], timeout = 3600)
        self.work_dir = "/var/www/flask/covid_iqs/"
        self.nlp = spacy.load("en_core_web_sm")
        self.tr = pytextrank.TextRank()  ###not support in the 03/2021 version. Please check back later
        self.nlp.add_pipe(self.tr.PipelineComponent, name="textrank", last=True)
        self.limit = 30

    def highlight_keyword (self, term_list, source):
        return source
    
    def query_elastic_search (self, term_list):
        query_terms = ""
        for term in term_list:
            query_terms+=' +"'+term+'"'
    
        res_list = self.es.search (index='nih_1', body = {
            "min_score":2,
            "query": {
                "multi_match": {
                "query": query_terms,
                "type": "best_fields", #best_fields, phrase
                "fields": ["title","abstract"], #meta_terms
                "tie_breaker": 0.3 
                }
            },
            "highlight" : {
                "pre_tags" : [""],
                "post_tags" : [""],
                "fields" : {
                    "title" : {},
                    "abstract": {}
                }
            }

        }, size = self.limit)
        return res_list
    
    def collect_query_term_data (self, term_list):
        res = self.query_elastic_search (term_list) 
        data = {}
        data['abstract'] = []
        data['summary'] = [
            {'total_return' : res['hits']['total']['value']}
        ]
        num_article = len (res['hits']['hits'])
        list_article_info_needed = res['hits']['hits'][0 : min (self.limit, num_article)]
        for article_info in list_article_info_needed:
            a_id = article_info ['_source']['a_id']
            score = article_info ['_score']
            highlight_title = None
            title = article_info['_source']['title']
            if ('title' in article_info['highlight']):
                title = self.highlight_keyword (term_list, title)

            highlight_abs = None
            abstract = article_info['_source']['abstract']
            if ('abstract' in article_info['highlight']):
                highlight_abs = article_info['highlight']['abstract']

            sentences=nltk.sent_tokenize(abstract)[0:3]
            first_para = ""
            for s in sentences:
                s = self.highlight_keyword (term_list, s)
                first_para += (s+"\n")

            if (len(abstract)>5): ### at least 5 words otherwises the system does not provide any key sentences
                if (highlight_abs):
                    for line in highlight_abs:
                        line = line.strip()
                        new_line= self.highlight_keyword (term_list,line)
                        abstract = abstract.replace(line, new_line) ### replace sentence with key term 
                        line = new_line

                t_file = self.work_dir + "static/process/textrank/" + str(a_id) + ".txt"
                if (os.path.isfile(t_file)):
                    f=open(t_file, "r",encoding='utf-8')
                    line_count = len(open(t_file,encoding='utf-8').readlines(  ))
                    read_count=2
                    current_count=0
                    for line in f:
                        if (current_count<=read_count):
                            line=line.strip()
                            new_line="<font color=blue>"+line+"</font>"
                            abstract = abstract.replace(line, new_line) ### replace key sentence with color  
                            current_count+=1
                        else:
                            break
                else:
                    print ("Textrank is not available now. Please check the website for the latest update.")
                    doc = self.nlp (str (abstract ))
                    for sent in doc._.textrank.summary(limit_phrases=20, limit_sentences=3):
                        key_sent=str(sent).strip()
                        new_line="<font color='blue'>"+key_sent+"</font>"
                        abstract = abstract.replace(key_sent, new_line) ### replace key sentence with color 
            
            condition = article_info['_source']['symp']
            cd = article_info['_source']['cd']
            target = article_info['_source']['target']
            device = article_info['_source']['device']

            doi = article_info['_source']['doi']
            publish_time = article_info['_source']['p_date']
            p_type = article_info['_source']['p_type']
            authors = article_info['_source']['authors']

            journal = article_info['_source']['journal']
            pubmed_id = article_info['_source']['pmid']
            source_x = article_info['_source']['source']
            citation_count = 0
            try:
                k = sql_query.find_citation_count (str (a_id))
                citation_count = int (k)
                print ("I am here " + str (k))
            except:
                citation_count = 0
            article_item = {
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
                'device':device,
                'first_para':first_para,
                'citation_count':citation_count
            }
            data['abstract'].append (article_item)
        return data

    def generate_query_term (self, user_id, term_list):
        data = self.collect_query_term_data (term_list)
        json_file_name = self.work_dir + "static/process/" + str(user_id) + "_999998.json"
        if (path.exists (json_file_name )):   
            os.remove (json_file_name)
        with open(json_file_name, 'w') as outfile:
            json.dump(data, outfile)
        

            
            
            


        
        
        