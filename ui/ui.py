import sys
sys.path.append('..') # This allows us to import from parent directory
version = sys.argv[1] # should be 'test' or 'prod'

import waitress
from flask import Flask, render_template, Response, request
import requests

from bedrock import stream_response

app = Flask(__name__)

from RAG_jiao.rag_main import RAG
from RAG_jiao.query_processing.query_processing import expand_course_code_in_query 
from RAG_jiao.query_processing.query_processing import expand_subject_abbreviation
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

import pickle
with open('../RAG_jiao/query_processing/course_code_to_name_dict.pkl', 'rb') as f:
    course_dict = pickle.load(f)

CUDA_DEVICE = 'cuda:6'
model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {"device": CUDA_DEVICE}
encode_kwargs = {"normalize_embeddings": True}
bge_emb = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

my_rag = RAG(cuda_device=CUDA_DEVICE)
my_rag.load_data_from_file('../RAG_jiao/data/Sem75-Complete.txt', 'full_data')
my_rag.load_data_from_file('../RAG_jiao/data/Sem75-Complete.txt', 'full_data_lemma', content_key='lemma')
print('Dataset loaded')

my_rag.create_dense_vector_index(bge_emb, 'bge_embedding', 'full_data')
my_rag.create_bm25_index('bm25_retriever', 'full_data_lemma', top_k=3)
print('Indexes created')

def get_similar_docs(q):
    q = expand_course_code_in_query(q, course_dict)
    q = expand_subject_abbreviation(q)

    # retrieve 3 with each retriever
    res = my_rag.dense_retrieval(q, 'bge_embedding', use_mmr=True, top_k=6)

    # retrieve 3 with each retriever
    res1 = my_rag.bm25_retrieval(q, 'bm25_retriever', if_lemmatize=True)

    # rerank
    hybrid_res = res + res1
    hybrid_res = my_rag.remove_duplicate_doc(hybrid_res)
    rerank_res = my_rag.rerank(q, hybrid_res)

    # choose
    rerank_res = rerank_res[:6]
    rerank_res = [res[0] for res in rerank_res]
    res_more_context = []
    ## For each semantically chunked chunk, we will also add the chunk following it to the context 
    ## semantically chunked chunks are indices 0-1648
    for chunk in rerank_res:
        if (chunk.metadata['seq_num'] < 1649) :
            res_more_context.append(chunk)
            res_more_context.append(my_rag.get_document('dataset', chunk.metadata['seq_num'] + 1))
        else :
            res_more_context.append(chunk)
    res_more_context = my_rag.remove_duplicate_doc(res_more_context)
    return [doc.page_content for doc in res_more_context]

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
Given the context information and not prior knowledge, answer the query. If the context does not contain enough information to answer to query, don't answer.
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