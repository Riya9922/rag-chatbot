import chromadb
import logging
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
DB_PATH = os.path.join(os.getcwd(), "data", "vector_db")
COLLECTION_NAME = "mf_facts_collection"

def get_vector_store():
    """
    Initialises and returns the local ChromaDB collection.
    """
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
        
    client = chromadb.PersistentClient(path=DB_PATH)
    logger.info(f"Connected to Local ChromaDB at {DB_PATH}")
    
    # Embedding Function (all-MiniLM-L6-v2)
    # This matches the model used in RAG_Architecture.md
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"} # Using cosine similarity for text
    )
    
    return collection

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    coll = get_vector_store()
    logger.info(f"Collection Ready: {COLLECTION_NAME}")
    logger.info(f"Current Count: {coll.count()} items")
