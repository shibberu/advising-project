import os
from langchain_text_splitters import HTMLHeaderTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import GPT4All
from langchain_community.document_loaders import PyPDFLoader

documents = []

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
]

# https://github.com/nomic-ai/gpt4all/blob/main/gpt4all-bindings/python/gpt4all/gpt4all.py
# GPT4AllEmbeddings is just using all-MiniLM-L6-v2.gguf2.f16.gguf behind the scenes
embedding_function = GPT4AllEmbeddings()

for root, dirs, files in os.walk('./dataset'):
    for file in files:
        full_path = f'{root}/{file}'
        if file.endswith(".pdf"):
            print('Loading', full_path)
            loader = PyPDFLoader(full_path)
            documents += loader.load_and_split()
        elif file.endswith(".html"):
            print('Loading', full_path)
            html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            documents += html_splitter.split_text_from_file(full_path)
vectorstore = Chroma.from_documents(documents=documents, embedding=embedding_function, persist_directory="./chroma_db")