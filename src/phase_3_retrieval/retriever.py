import os
from dotenv import load_dotenv
from src.phase_2_indexing.vector_store import get_vector_store

load_dotenv()

class MFRetriever:
    def __init__(self, top_k=5):
        self.collection = get_vector_store()
        self.top_k = top_k

    def retrieve(self, query, fund_filter=None):
        """
        Retrieves top-k relevant chunks from Chroma Cloud.
        Optional fund_filter can be a string (e.g., 'HDFC Mid Cap')
        """
        where_clause = {}
        if fund_filter:
            where_clause = {"fund_name": {"$contains": fund_filter}}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=self.top_k,
            where=where_clause if where_clause else None
        )
        
        # Format the results for the LLM
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                
                formatted_results.append({
                    "content": doc,
                    "source": metadata.get("url", "Official Data"),
                    "fund": metadata.get("fund_name", "N/A"),
                    "nav": metadata.get("nav", "N/A"),
                    "updated": metadata.get("scraped_at", "Unknown")
                })
        
        return formatted_results

if __name__ == "__main__":
    # Test Retrieval
    retriever = MFRetriever()
    test_query = "What is the NAV of HDFC Mid Cap Fund?"
    facts = retriever.retrieve(test_query)
    
    print(f"--- Retrieved {len(facts)} facts for: '{test_query}' ---")
    for fact in facts:
        print(f"[{fact['fund']}] {fact['content'][:100]}...")
