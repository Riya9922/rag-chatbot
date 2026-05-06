import json
import os
import logging
from src.phase_2_indexing.vector_store import get_vector_store
from datetime import datetime

logger = logging.getLogger(__name__)

# Input/Output paths
RAW_DATA_DIR = os.path.join(os.getcwd(), "data", "raw")

def chunk_content(text, chunk_size=800, overlap=100):
    """
    Split text into overlapping chunks.
    """
    chunks = []
    if not text:
        return chunks
    
    # Simple recursive-style split on newlines first
    paragraphs = text.split("\n")
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Handle cases where a single paragraph is too large
            if len(p) > chunk_size:
                for i in range(0, len(p), chunk_size - overlap):
                    chunks.append(p[i : i + chunk_size])
                current_chunk = ""
            else:
                current_chunk = p + "\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def run_ingestion():
    """
    Reads all raw JSON files and populates the vector store.
    """
    logger.info(f"Starting Ingestion Pipeline...")
    collection = get_vector_store()
    
    if not os.path.exists(RAW_DATA_DIR):
        logger.error("Raw data directory not found — aborting ingestion.")
        return

    files_processed = 0
    total_chunks = 0
    fund_summaries = []
    
    for filename in os.listdir(RAW_DATA_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(RAW_DATA_DIR, filename)
            with open(file_path, "r", encoding='utf-8') as f:
                fund_data = json.load(f)
            
            content = fund_data.get("content", "")
            metadata_base = fund_data.get("metadata", {})
            
            # Collect for summary
            fund_summaries.append(metadata_base)
            
            # Generate Chunks
            chunks = chunk_content(content)
            
            if not chunks:
                logger.warning(f"Skipping {filename}: No content chunks generated.")
                continue

            # Prepare for ChromaDB
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [metadata_base for _ in range(len(chunks))]
            
            # Upsert into collection
            collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            
            total_chunks += len(chunks)
            files_processed += 1
            logger.info(f"Indexed {filename}: {len(chunks)} chunks")

    # Save master summary
    summary_path = os.path.join(os.getcwd(), "data", "fund_summary.json")
    with open(summary_path, "w", encoding='utf-8') as f:
        json.dump(fund_summaries, f, indent=4, ensure_ascii=False)
    logger.info(f"Saved fund summary to {summary_path}")

    logger.info(f"Ingestion Finished. Files: {files_processed}, Total Chunks: {total_chunks}")

if __name__ == "__main__":
    run_ingestion()
