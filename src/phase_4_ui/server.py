from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import re
from src.phase_3_retrieval.retriever import MFRetriever
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
retriever = MFRetriever()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Query(BaseModel):
    question: str

# --- Refusal Detection Logic ---
ADVISORY_KEYWORDS = ["better", "best", "should i", "recommend", "buy", "sell", "advice", "opinion", "compare"]

def is_advisory(query: str):
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in ADVISORY_KEYWORDS)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("src/phase_4_ui/index.html", "r") as f:
        return f.read()

@app.post("/query")
def process_query(query: Query):
    try:
        # 1. Check for Advisory/Opinion
        if is_advisory(query.question):
            return {
                "answer": "As a factual Mutual Fund Assistant, I am unable to provide investment advice or opinions. For official guidance, please visit the SEBI or AMFI websites.",
                "source": "https://investor.sebi.gov.in/",
                "last_updated": "N/A"
            }

        # 2. Retrieve Facts from Chroma Cloud
        facts = retriever.retrieve(query.question)
        
        if not facts:
            return {
                "answer": "I'm sorry, I couldn't find specific factual data for that query in my current database.",
                "source": None,
                "last_updated": None
            }

        # 3. Generate Factual Response with OpenAI
        context_text = "\n\n".join([f"Source: {f['source']}\nContent: {f['content']}" for f in facts])
        
        AVAILABLE_FUNDS = [
            "HDFC Mid-Cap Opportunities Fund",
            "HDFC Equity Fund (Flexi Cap)",
            "HDFC Focused 30 Fund",
            "HDFC ELSS Tax Saver Fund",
            "HDFC Top 100 Fund (Large Cap)"
        ]

        prompt = f"""
        You are a factual Mutual-Fund FAQ assistant. 
        
        CRITICAL RULES:
        1. GENERAL KNOWLEDGE EXCEPTION: If the user is asking for a general definition or general knowledge (e.g. "what does SIP mean?", "what is NAV?", "how do mutual funds work?"), YOU MUST ANSWER IT directly using your own general knowledge. Be concise.
        2. MISSING FUND EXCEPTION: If the user is asking for a specific metric (like the NAV value, the fund size, the minimum SIP amount) but DOES NOT specify which mutual fund they are asking about, DO NOT guess or proactively provide an answer for a random fund.
        3. Instead, DO NOT ANSWER the metric question. Simply reply stating that you need them to specify a fund and provide this list of options for them to choose from: {', '.join(AVAILABLE_FUNDS)}.
        4. If the question is clear and specifies a fund, answer in 3 sentences or less, be strictly objective, and use ONLY the provided Context. Mention the NAV if available.

        Context:
        {context_text}

        User Question: {query.question}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "You are a factual financial data assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )

        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "source": facts[0]["source"],
            "last_updated": facts[0]["updated"]
        }
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(trace)
        return {
            "answer": f"Backend Error: {str(e)}",
            "source": None,
            "last_updated": None
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
