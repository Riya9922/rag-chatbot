import chromadb
from chromadb.utils import embedding_functions
import os
import shutil
DB_PATH = "data/vector_db"
COLLECTION_NAME = "fund_facts"

def get_vector_store():
    # Vercel's serverless functions have a read-only filesystem except for /tmp
    is_vercel = os.getenv("VERCEL") == "1"
    current_db_path = DB_PATH
    
    if is_vercel:
        tmp_db_path = "/tmp/vector_db"
        if not os.path.exists(tmp_db_path):
            if os.path.exists(DB_PATH):
                shutil.copytree(DB_PATH, tmp_db_path)
            else:
                os.makedirs(tmp_db_path)
        current_db_path = tmp_db_path
    else:
        if not os.path.exists(DB_PATH):
            os.makedirs(DB_PATH)
    
    # Using local embedding function
    client = chromadb.PersistentClient(path=current_db_path)
    
    # default embedding function is all-MiniLM-L6-v2 (using onnxruntime instead of heavy torch)
    embedding_func = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    
    return collection

if __name__ == "__main__":
    collection = get_vector_store()
    print(f"Collection '{COLLECTION_NAME}' initialised. Current count: {collection.count()}")
