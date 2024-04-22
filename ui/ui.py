import sys
sys.path.append('..') # This allows us to import from parent directory
version = sys.argv[1] # should be 'test' or 'prod'

import waitress
from flask import Flask, render_template, Response, request
import requests

from bedrock import stream_response

app = Flask(__name__)

from RAG_jiao.jiao_rag import RAG
from RAG_jiao.query_processing import expand_course_code_in_query 
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

import pickle
with open('../RAG_jiao/util/course_code_to_name_dict.pkl', 'rb') as f:
    course_dict = pickle.load(f)

model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {"device": 'cuda:1'}
encode_kwargs = {"normalize_embeddings": True}
bge_emb = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

my_rag = RAG(cuda_device='cuda:6')
my_rag.load_data_from_file('../RAG_jiao/data/new_complete_dataset_credit_replaced.txt', 'full_data')
my_rag.load_data_from_file('../RAG_jiao/data/new_complete_dataset_credit_replaced.txt', 'full_data_lemma', content_key='lemma')
print('Dataset loaded')

my_rag.create_dense_vector_index(bge_emb, 'bge_embedding', 'full_data')
my_rag.create_bm25_index('bm25_retriever', 'full_data_lemma')
print('Indexes created')

def get_similar_docs(q):
    q = expand_course_code_in_query(q, course_dict)
    res = my_rag.dense_retrieval(q, 'bge_embedding', use_mmr=True)
    res1 = my_rag.bm25_retrieval(q, 'bm25_retriever', if_lemmatize=True)
    hybrid_res = res + res1
    rerank_res = my_rag.rerank(q, hybrid_res)
    return [doc[0].page_content for doc in rerank_res]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    query = data['query']

    context = '\n'.join(get_similar_docs(query))

    # Prompt template as recommended here: https://docs.mistral.ai/guides/basic-RAG/
    prompt = f"""You are an AI academic advisor for Rose-Hulman. Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query}
Answer:
"""

    return Response(stream_response(prompt, 256), content_type='text/plain')

if version == 'prod':
    waitress.serve(app, host='0.0.0.0', port=5000)
elif version == 'test':
    waitress.serve(app, host='0.0.0.0', port=5001)
else:
    print('Invalid version:', version)