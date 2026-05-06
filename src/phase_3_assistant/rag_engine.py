import os
import openai
from src.phase_2_indexing.vector_store import get_vector_store
from src.phase_3_assistant.refusal_handler import check_for_advice, get_refusal_message
from dotenv import load_dotenv

load_dotenv()

def generate_answer(query):
    """
    Coordinates the RAG flow:
    1. Check for advice (Refusal Handling)
    2. Retrieve relevant chunks (Retrieval)
    3. Construct prompt and call LLM (Generation)
    """
    
    # 1. Refusal Detection
    if check_for_advice(query):
        return {
            "answer": get_refusal_message(),
            "source": "System Policy",
            "date": "N/A",
            "is_refusal": True
        }

    try:
        # 2. Retrieval
        collection = get_vector_store()
        # Query for top 3 matches
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        if not results['documents'][0]:
            return {
                "answer": "I'm sorry, I couldn't find any factual information regarding that query in the official HDFC fund documents I have indexed.",
                "source": "None",
                "date": "N/A",
                "is_refusal": False
            }

        context = "\n---\n".join(results['documents'][0])
        # Use metadata from the top result
        top_meta = results['metadatas'][0][0]
        source_url = top_meta.get("url", "Unknown Source")
        updated_date = top_meta.get("scraped_at", "Unknown Date")

        # 3. Generation (LLM)
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        system_instr = (
            "You are a strict Factual Mutual Fund Assistant. "
            "Provide a concise answer (max 3 sentences) using ONLY the provided context. "
            "If the answer isn't in the context, say you don't know. "
            "NEVER provide investment advice or personal opinions."
        )
        
        prompt = f"Context:\n{context}\n\nUser Question: {query}\n\nFactual Answer:"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-4o for higher accuracy
            messages=[
                {"role": "system", "content": system_instr},
                {"role": "user", "content": prompt}
            ],
            temperature=0, # Deterministic facts
            max_tokens=200
        )
        
        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "source": source_url,
            "date": updated_date,
            "is_refusal": False
        }

    except Exception as e:
        print(f"RAG Engine Error: {e}")
        return {
            "answer": f"An error occurred while processing your request: {e}",
            "source": "System Error",
            "date": "N/A",
            "is_refusal": False
        }
