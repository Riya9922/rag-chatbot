import chromadb
from chromadb.utils import embedding_functions
import os

DB_PATH = "data/vector_db"
COLLECTION_NAME = "fund_facts"

def get_vector_store():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    
    # Using local embedding function
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # default embedding function is all-MiniLM-L6-v2
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    
    return collection

if __name__ == "__main__":
    collection = get_vector_store()
    print(f"Collection '{COLLECTION_NAME}' initialised. Current count: {collection.count()}")
