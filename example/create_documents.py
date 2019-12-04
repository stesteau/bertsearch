"""
Example script to create elasticsearch documents.
"""
import argparse
import json
import os 
import pandas as pd

from bert_serving.client import BertClient
bc = BertClient(output_fmt='list')


def create_document(doc, emb, index_name):
    return {
        '_op_type': 'index',
        '_index': index_name,
        'text': doc['txt'],
        'title': doc['head'],
        'docno': doc['doc_no'],
        'text_vector': emb
    }


def load_dataset(path):
    docs = []
    df = pd.read_csv(path)
    for row in df.iterrows():
        series = row[1]
        doc = {
            'title': series.Title,
            'text': series.Description
        }
        docs.append(doc)
    return docs



def bulk_predict(docs, batch_size=256):
    """Predict bert embeddings."""
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i: i+batch_size]

        embeddings = bc.encode([doc['txt']+" "+doc['head'] for doc in batch_docs])
        for emb in embeddings:
            yield emb


def main(args):
    if os.path.exists('documents.json'):
        with open('documents.json', 'r') as f:
            docs = json.load(f)


    with open(args.save, 'w') as f:
        count = 0
        for doc, emb in zip(docs, bulk_predict(docs)):
            count = count + 1
            print("indexing shizzile \n")
            d = create_document(doc, emb, args.index_name)
            f.write(json.dumps(d) + '\n')
            if(count > 1): 
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating elasticsearch documents.')
    parser.add_argument('--data', help='data for creating documents.')
    parser.add_argument('--save', default='embeddings.jsonl', help='created documents.')
    parser.add_argument('--index_name', default='news', help='Elasticsearch index name.')
    args = parser.parse_args()
    main(args)
