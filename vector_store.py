__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import gc
import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class MemoryBank:
    def __init__(self):
        self.path = "./chroma_db"
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None

    def ingest_knowledge(self):
        folder = './knowledge'
        if not os.path.exists(folder): os.makedirs(folder)
        
        docs = DirectoryLoader(folder, glob="*.pdf", loader_cls=PyPDFLoader).load() + \
               DirectoryLoader(folder, glob="*.txt", loader_cls=TextLoader).load()
        
        if not docs: return "Nenhum arquivo encontrado."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
        chunks = text_splitter.split_documents(docs)
        
        self.vector_store = Chroma.from_documents(chunks, self.embeddings, persist_directory=self.path)
        return f"{len(chunks)} fragmentos integrados com sucesso."

    def get_context(self, query):
        if os.path.exists(self.path) and not self.vector_store:
            self.vector_store = Chroma(persist_directory=self.path, embedding_function=self.embeddings)
        if self.vector_store:
            results = self.vector_store.similarity_search(query, k=7)
            return "\n\n--- TRECHO ---\n\n".join([doc.page_content for doc in results])
        return ""

    def clear_memory(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            
        folder = './knowledge'
        if os.path.exists(folder):
            for f in os.listdir(folder):
                os.unlink(os.path.join(folder, f))
                
        self.vector_store = None
        gc.collect()
        
        return " Memória Apagada"