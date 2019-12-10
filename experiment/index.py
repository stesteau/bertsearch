import lucene
import os
import re
import argparse

from bs4 import BeautifulSoup
import lxml
import gzip 

from java.nio.file import Paths
import json
from elasticsearch import Elasticsearch, helpers

BASE_PATH = '/home/seb/Desktop/master/INF8883_NLP/data/TREC-AP88-90-qrels1-50/'
base_dir = '/home/seb/Desktop/master/INF8883_NLP/'
trec_path = ''


# just a simple function to output a progressbar during indexing
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


def parse():
    dataset = 'data/TREC-AP88-90-qrels1-50/AP/'
    path = base_dir+dataset
    files_to_index = os.listdir(path)
    length = len(files_to_index)
    print("Parsing %d files" % (length))

    documents = []
    count = 0
    for index, TrecFile in enumerate(files_to_index):        
        #gz = gzip.GzipFile(os.path.join(base_dir, dataset, file))
        with gzip.GzipFile(os.path.abspath(os.path.join(path,TrecFile))) as docfile:

            contents = docfile.read()
            xml = '<ROOT>' + str(contents) + "</ROOT>"
            root = BeautifulSoup(xml, 'xml')            

            printProgressBar(index, length, TrecFile+"[", "]")

            for doc in root.find_all('DOC'):
                tmp = {}
                if doc.find('HEAD') is not None:
                    tmp['title'] = doc.find('HEAD').text.strip()

                if doc.find('DOCNO') is not None:
                    tmp['doc_no'] = doc.find('DOCNO').text.strip()

                for text_el in doc.find_all('TEXT'):
                    tmp['text'] = text_el.text.strip().rstrip().replace("\r"," ").replace('\t',' ').replace('\n',' ')  

                count = count+1
                documents.append(tmp)

    print("Done parsing %d documents" % (count))
    if os.path.isfile('documents.json'):
        os.remove("documents.json")
    with open('documents.json', 'w') as json_file:        
        json.dump(documents, json_file)
    return documents


def index(documents, analyzer="baseline", similarity="classic"):

    idx_name = analyzer.lower()+"_"+similarity.lower()
    filename = "schema/"+ idx_name + ".json"
    with open(filename, 'r') as f:
        datastore = json.load(f)

    print("file: " + filename + "\n")
    es = Elasticsearch()
    es.indices.delete(index=idx_name, ignore=[400, 404])
    es.indices.create(index=idx_name, ignore=400, body=datastore)  

    print("created index, now indexing...\n" )   
    results = helpers.streaming_bulk(es, documents, index=idx_name, chunk_size=50)
    for status, r in results:
        if not status:
            print("index err result %s", r) 


    #index the shizzle
    print("Done indexeing "+ "\n")

if __name__ == "__main__":

    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    parser = argparse.ArgumentParser(description="Make some lucene indexes")
    parser.add_argument("-a", "--all", const="all", nargs="?", required=False)
    parser.add_argument("indextype", type=str, default="better", nargs='?')
    parser.add_argument('similarity', type=str, default="bm25", nargs='?')
    args = parser.parse_args()

    if os.path.isfile('documents.json'):
        with open('documents.json', 'r') as f:
            documents = json.load(f)
    else:
        documents = parse()

    if(args.all):
        for analyzer in ['baseline', 'better']:
            for sim in ['classic', 'bm25']:
                index(documents, analyzer, sim)
                print("Done\n")
    else:
        index(documents, args.indextype, args.similarity)