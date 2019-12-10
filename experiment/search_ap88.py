# -*- coding: utf-8 -*-
"""
@author: stesteau
# """
import io, os, sys
import gzip 
import pickle
import re
import codecs
import random
import math
import string
import operator
import multiprocessing
import numpy as np
from compiler.ast import flatten 
import matplotlib.pyplot as plt
from collections import Counter
import time
import argparse
from elasticsearch import Elasticsearch

clean = lambda t: re.sub('[^&\.a-z0-9]', ' ', t.strip())
base_dir = '/home/seb/Desktop/master/INF8883_NLP/data/trec_req/'

 # 007# U.S. Budget Deficit 
def parse_topics(filename, index_name):        
    es_conn = Elasticsearch()
    with open(os.path.join(base_dir,filename), 'r') as f:
        output_file = filename.replace(".txt", "_" + index_name + "_retrieved.txt")
        print "writing results to " + os.path.join(base_dir,output_file) + "\n"
        with open(os.path.join(base_dir,output_file), 'w') as output:
            for line in f:
                tokens = line.strip('+-=&&||><!()[]^"~*?:\/').split('#')
                tokens = map(str.strip, tokens)
                search_terms = ' '.join(tokens[1:])
                count = 1
                for doc_no, score in search(search_terms, es_conn, index_name):
                    output.write('{} {} {} {} {} t1\n'.format(int(tokens[0]), 0, doc_no, count, score))
                    count += 1

def search(query_string, es_conn, index_name):
    #print query_string + "\n"
    q = re.sub('([{}])'.format(re.escape('\\+\-&|!(){}\[\]^~*?:\/')), r"\\\1", query_string)
    res = es_conn.search(index = index_name,
        body = {
            "_source": ["doc_no"],
            "query": {
                "query_string": {
                    "query": q,
                }
            },
            "size" : 1000
        }, ignore=400
    )
    for hit in res['hits']['hits']:
        doc_no = hit["_source"]["doc_no"]
        score = hit["_score"]
        yield (doc_no, score)

def run(args):    
    parse_topics('requetesCourtes.txt', 'baseline-news')   
    parse_topics('requetesLongues.txt', 'baseline-news')
    parse_topics('requetesCourtes.txt', 'baseline-news_tfidf')   
    parse_topics('requetesLongues.txt', 'baseline-news_tfidf')
    parse_topics('requetesCourtes.txt', 'news')   
    parse_topics('requetesLongues.txt', 'news')
    parse_topics('requetesCourtes.txt', 'news_tfidf')   
    parse_topics('requetesLongues.txt', 'news_tfidf')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='INF8883 Homework')
    schema_choices=['baseline', 'analysis', 'all']
    parser.add_argument('--schema', type=str, default='all', choices=schema_choices, help='type of schema used for the indexing')
    schema_choices=['tfidf','bm25']
    parser.add_argument('--ponderation', type=str, default='tfidf', help='ponderation used for data')
    args = parser.parse_args()
    run(args)


    