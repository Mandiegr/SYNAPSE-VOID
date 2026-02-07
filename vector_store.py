__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import gc
import shutil

# temporário: Garante execução estável em CPUs e silencia conflitos de driver
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class MemoryBank:
    def __init__(self):
        self.path = "./chroma_db"
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vector_store = None

    def ingest_knowledge(self):
        folder = './knowledge'
        if not os.path.exists(folder): os.makedirs(folder)
        
        loader = DirectoryLoader(folder, glob="*.pdf", loader_cls=PyMuPDFLoader)
        docs = loader.load()

        if not docs: return "Nenhum PDF encontrado para indexar."

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            import time; time.sleep(1)

        self.vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings, 
            persist_directory=self.path
        )
        return f"Sucesso: {len(chunks)} fragmentos integrados na CPU."

    def get_context(self, query):
        if not os.path.exists(self.path): return ""
        if not self.vector_store:
            self.vector_store = Chroma(persist_directory=self.path, embedding_function=self.embeddings)
        
        results = self.vector_store.similarity_search(query, k=5)
        return "\n\n".join([doc.page_content for doc in results])

    def clear_memory(self):
        if os.path.exists(self.path): shutil.rmtree(self.path)
        if os.path.exists('./knowledge'):
            for f in os.listdir('./knowledge'): os.unlink(os.path.join('./knowledge', f))
        self.vector_store = None
        gc.collect()
        return "Memória limpa."