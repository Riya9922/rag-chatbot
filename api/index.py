import sys
import os

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.vector_store import get_vector_store
from src.refusal_handler import is_advisory_query, get_refusal_response
from groq import Groq

load_dotenv()

app = FastAPI()

# Allow CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    source_url: str = None
    scraped_at: str = None

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    # 1. Refusal Handling
    if is_advisory_query(query):
        return ChatResponse(response=get_refusal_response())
        
    # 2. RAG Retrieval
    try:
        collection = get_vector_store()
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        context = "\n".join(results['documents'][0])
        source_url = results['metadatas'][0][0]['url'] if results['metadatas'][0] else "Unknown"
        scraped_at = results['metadatas'][0][0]['scraped_at'] if results['metadatas'][0] else "N/A"
        
        # 3. LLM Generation
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        system_prompt = (
            "You are a factual Mutual Fund FAQ assistant. Answer ONLY based on the provided context. "
            "Limit your response to a maximum of 3 sentences. Do not provide advice or opinions."
        )
        
        prompt = f"Context:\n{context}\n\nQuestion: {query}"
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        raw_answer = completion.choices[0].message.content
        
        return ChatResponse(
            response=raw_answer,
            source_url=source_url,
            scraped_at=scraped_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
