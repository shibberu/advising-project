import torch

def metadata_func(record: dict, metadata: dict):
        metadata['src'] = record.get('source')
        return metadata


class RAG():
    '''
    Usage:
    1. Load data from file
    2. Build dense vector index and/or create bm25 index
    3. Query. rerank if needed
    '''

    import torch
    
    def __init__(self, cuda_device):
        '''
        @param cuda_device: what cuda device to use
        '''
        self.data = {}
        self.cuda_device = cuda_device
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.dense_store = {}
        self.dense_retriever = {}
        self.dense_retriever_mmr = {}


        self.bm25 = {}
        # rerank
        self.reranker_tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-large')
        model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-large')
        self.reranker = model.to(torch.device(cuda_device))
        self.reranker.eval()
        from nltk.stem import WordNetLemmatizer
        self.lemmatizer = WordNetLemmatizer()

    def load_data_from_file(self, filepath, dataset_name, json_lines=True, content_key='text', metadata_function=metadata_func):
        '''
        Loads data from a file
        @param filepath: path to the file
        @param dataset: name of the dataset
        @param json_lines: whether the file is jsonlines. Refer to the documentation of Langchain's JSONLoader
        @param content_key: key to the document content. Refer to the documentation of Langchain's JSONLoader
        @param metadata_function: used to extract metadata. Refer to the documentation of Langchain's JSONLoader
        '''
        from langchain_community.document_loaders import JSONLoader
        import json
        data_loader = JSONLoader(
            file_path=filepath,
            jq_schema='.',
            content_key=content_key,
            text_content=False,
            json_lines=json_lines,
            metadata_func=metadata_function
        )

        self.data[dataset_name] = data_loader.load()

    def get_document(self, dataset_name, seq_num):
        if not (dataset_name in self.data):
            print(f'{dataset_name} has not been loaded yet')
            return 
        return self.data[dataset_name][seq_num - 1]

    def create_dense_vector_index(self, emb, retriever_name, dataset_name):
        '''
        Builds a dense vector index (database)
        @param emb: the embedding model/function to use 
        @param retriever_name: name of the retriever that uses the index. You will use this name to query 
        @param dataset_name: name of the dataset to build index on 
        '''
        from langchain_community.vectorstores import Chroma
        if not (dataset_name in self.data):
            print(f'{dataset_name} has not been loaded yet')
            return 
        self.dense_store[retriever_name] = Chroma.from_documents(self.data[dataset_name], emb)

    def dense_retrieval(self, query, retriever_name, top_k=3, use_mmr=True):
        '''
        Performs dense retrievals
        @param query: in natural language
        @param retriever_name: name of the retriever, specified when calling create_dense_vector_index()
        @param top_k: top k documents to retrieve
        @param use_mmr: whether to use mmr retrieval
        '''
        
        if not (retriever_name in self.dense_store):
            print(f'{retriever_name} has not been built yet')
            return 
        retr = None
        if use_mmr:
            retr = self.dense_store[retriever_name].as_retriever(search_type='mmr', search_kwargs={'k': top_k})
        else:
            retr = self.dense_store[retriever_name].as_retriever(search_kwargs={'k': top_k})
        res = retr.get_relevant_documents(query)
        return res

    def create_bm25_index(self, retriever_name, dataset_name, top_k=3):
        '''
        Initializes the bm25 retriever on a dataset
        @param retriever_name: name of the retriever that uses the index. You will use this to query
        @param dataset_name: name of the dataset to retrieve from
        @param top_k: top k documents to retrieve
        '''
        from langchain_community.retrievers import BM25Retriever
        if not (dataset_name in self.data):
            print(f'{dataset_name} has not been loaded yet')
            return 
        self.bm25[retriever_name] = BM25Retriever.from_documents(self.data[dataset_name], k=top_k)

    def bm25_retrieval(self, query, retriever_name, if_lemmatize=True):
        '''
        Performs bm25 retrieval
        @param query
        @param retriever_name: name of the retriever, specified when calling create_bm25_index()
        @param if_lemmatize: whether to lemmatize the query
        '''
        if (if_lemmatize) :
            lemm_words = []
            lmtz = self.lemmatizer
            for w in query.split(' '):
                lemm_words.append(lmtz.lemmatize(w))
            query = ' '.join(lemm_words)
            
        if not (retriever_name in self.bm25):
            print(f'{retriever_name} has not been initialized yet')
            return 
        
        res = self.bm25[retriever_name].get_relevant_documents(query)
        return res

    def rerank(self, query, docs):
        '''
        Reranks documents using bge reranker
        @param query
        @param docs: documents
        '''
        pairs = []
        for doc in docs:
            pairs.append([query, doc.page_content])
        scores = []
        with torch.no_grad():
            inputs = self.reranker_tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            inputs = inputs.to(torch.device(self.cuda_device))
            scores = self.reranker(**inputs, return_dict=True).logits.view(-1, ).float()
        scores = scores.cpu().numpy()
        doc_and_score = []
        for i in range(0, len(scores)):
            doc_and_score.append([docs[i], scores[i]])
        
        # sort
        doc_and_score.sort(key=lambda x: -x[1])
        del inputs
        return doc_and_score

    def remove_duplicate_doc(self, docs, identity_func=None):
        '''
        remove duplicate documents
        @param identity_func: used to identify a document
        '''
        def local_id_func(doc):
            return doc.metadata['seq_num']
        if (identity_func == None):
            identity_func = local_id_func
        res = []
        seen = set()
        for doc in docs:
            if (identity_func(doc) in seen):
                pass
            else:
                seen.add(identity_func(doc))
                res.append(doc)
        return res


    
    
# tmp = pd.read_json(path_or_buf='./data/student_hb_HSSA_req_chunk200_overlap20_lemma.jsonl', lines=True)
# tmp.to_json('./data/pdf_with_lemm.json')