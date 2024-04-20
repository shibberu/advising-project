import sys
version = sys.argv[1] # should be 'test' or 'prod'

import waitress
from flask import Flask, render_template, Response, request
import requests
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma

from bedrock import stream_response

app = Flask(__name__)

embedding_function = GPT4AllEmbeddings()
vectorstore = Chroma(embedding_function=embedding_function, persist_directory="./chroma_db")

def get_similar_docs(query):
    embedding = embedding_function.embed_query(query)
    return [doc.page_content for doc in vectorstore.similarity_search_by_vector(embedding)]

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