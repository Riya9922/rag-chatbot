import json
import os
from src.vector_store import get_vector_store

DATA_DIR = "data/raw"

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    # Simple fixed-size chunking for now
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def ingest_data():
    collection = get_vector_store()
    
    if not os.path.exists(DATA_DIR):
        print(f"No data directory found at {DATA_DIR}")
        return

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r") as f:
                fund_data = json.load(f)
            
            raw_text = fund_data.get("raw_text", "")
            fund_name = fund_data.get("fund_name", filename)
            url = fund_data.get("url", "")
            scraped_at = fund_data.get("scraped_at", "")

            chunks = chunk_text(raw_text)
            
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{
                "fund_name": fund_name,
                "url": url,
                "scraped_at": scraped_at,
                "source": filename
            } for _ in range(len(chunks))]
            
            # Batch upsert
            collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"Ingested {len(chunks)} chunks for {fund_name}")

if __name__ == "__main__":
    ingest_data()
