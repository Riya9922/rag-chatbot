# RAG Architecture for Mutual Fund FAQ Assistant (Facts‑Only)

---

## 1. Overview
The system is a **Retrieval‑Augmented Generation (RAG)** chatbot that answers **factual** queries about mutual‑fund schemes using only **official public sources** (AMC websites, AMFI, SEBI).  Every response is limited to three sentences, includes a single citation link, and a footer with the "last‑updated" date.  Advisory or opinion‑based queries are refused with a polite message and an educational link.

---

## 2. High‑Level Components
```mermaid
flowchart TD
    A[Official Sources] -->|Scrape / Download| B[Ingestion Pipeline]
    B --> C[Chunking & Text Normalisation]
    C --> D[Embedding Model]
    D --> E[Vector Store (Chroma Cloud)]
    E --> F[Retriever Service]
    F --> G[Prompt Builder]
    G --> H[LLM Generator]
    H --> I[Response Formatter]
    I --> J[User Interface]
    H --> K[Refusal Detector]
    K --> I
    subgraph Multi‑Thread
        J --> L[Conversation Manager]
        L --> F
    end
```

---

## 3. Data & Source Layer
| Source | Example URLs | Notes |
|--------|---------------|-------|
| **AMC website** | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth`, `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth`, `https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth`, `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth`, `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` | Schemes factsheets for HDFC funds |
| **AMFI** | `https://www.amfiindia.com/` | Mutual‑fund regulations, tax guidance |
| **SEBI** | `https://www.sebi.gov.in/` | Legal definitions, compliance docs |

*Only these official domains are permitted. No third‑party blogs or aggregators.*

---

## 4. Ingestion Pipeline
1. **Scraping Service** – Managed via **GitHub Actions**; runs daily at **03:45 UTC (09:15 AM IST)** to fetch latest content from the defined corpus URLs.
2. **HTML → Markdown** – Strip navigation, ads, and scripts; keep only textual content (tables, headings, bullet lists).
3. **Metadata Enrichment** – Store source URL, retrieval‑date, and key factual metrics (NAV, Minimum SIP, Fund Size, Expense Ratio, Rating) in the document metadata.
4. **Structured Storage**:
   - **Vector Store Metadata**: These 5 key fields are attached to every chunk to enable precision retrieval and filtering.
   - **Summary JSON**: A master `fund_summary.json` is generated for rapid UI display of key metrics.
5. **Storage** – Raw markdown files and structured JSON are persisted in `data/`.

---

## 5. Chunking & Indexing
* **Chunk Size** – 300‑500 characters with overlap of 50 characters to preserve context across tables.
* **Pre‑processing** – Normalise whitespace, remove non‑ASCII symbols, keep numbers (e.g., expense‑ratio) intact.
* **Embedding Model** – `sentence‑transformers/all‑mpnet‑base‑v2` (or any open‑source model that fits the deployment constraints).  Embeddings are stored as 768‑dimensional vectors.
* **Vector Store** – **ChromaDB** (local, persisted on disk) with metadata fields `{url, scheme_id, doc_type, chunk_id}`.

---

## 6. Retrieval Service
* **Similarity Search** – Cosine similarity, top‑k = 5.
* **Hybrid Filter** – Optional filter on metadata (e.g., `scheme_id = XYZ`) when the user explicitly mentions a scheme.
* **Reranking** – A lightweight LLM‑based relevance scorer (e.g., `gpt‑2‑small`) to ensure the most factual chunk is first.

---

## 7. Prompt Engineering & Generation
**Prompt Template** (system prompt + retrieved chunks + user query):
```
You are a factual Mutual‑Fund FAQ assistant. Use ONLY the provided context to answer the user’s question. 
- Answer in ≤ 3 sentences.
- Include exactly ONE citation link (use the URL from the context).
- End with "Last updated from sources: <date>".
- Do NOT provide advice, opinions, or comparisons.

Context:
{retrieved_chunks}

User: {question}
```
The LLM (e.g., `gpt‑4o‑mini` or an open‑source Llama 2 13B) generates the response.

---

## 8. Refusal Detector
A **classifier** runs before prompt generation:
1. Detect if the query is advisory, speculative, or comparative.
2. If detected, skip retrieval and generate a refusal using the template:
```
I’m sorry, but I can only provide factual information about mutual‑fund schemes. 
For guidance on investment decisions, please refer to the official resources:
- AMFI: https://www.amfiindia.com/
- SEBI: https://www.sebi.gov.in/
```
The detector can be a simple rule‑based regex (e.g., keywords *invest, recommend, best, compare*) combined with a tiny LLM classifier.

---

## 9. User Interface (Minimal)
* **Welcome Banner** – "Welcome to the Mutual‑Fund FAQ Assistant (Facts‑Only)".
* **Example Queries** – three sample buttons (Expense ratio, Minimum SIP amount, Download statement).
* **Disclaimer Footer** – "Facts‑Only. No investment advice."
* Built with **Streamlit** (Python) or **React** + **FastAPI** backend.
* UI only displays the generated answer and citation; no user data is stored.

---

## 10. Multi‑Thread / Conversation Management
* Each chat session gets a **UUID** stored in a short‑lived in‑memory dictionary.
* Retrieval is stateless; the conversation manager only tracks the latest **conversation_id** to isolate contexts.
* Supports simultaneous independent sessions (e.g., via WebSocket rooms or FastAPI background tasks).

---

## 11. Security & Privacy Guarantees
| Requirement | Implementation |
|-------------|----------------|
| **No PII collection** | Front‑end never asks for PAN, Aadhaar, OTP, email, or phone. Backend validates that request bodies contain only `question` string.
| **Data‑at‑rest encryption** | Vector store folder encrypted with OS‑level file permissions (read/write for the service user only).
| **Data‑in‑transit** | HTTPS (TLS 1.3) for all API calls.
| **Audit Logging** | Minimal logs: timestamp, conversation_id, request hash (no user content), response status.

---

## 12. Deployment Considerations
* **Containerisation** – Docker image with Python 3.11, ChromaDB, and the LLM inference server.
* **Scalability** – Horizontal scaling of the API service; vector store can be shared via a network‑mounted volume.
* **Monitoring** – Prometheus metrics for request latency, retrieval hit‑rate, refusal‑rate.
* **CI/CD** – Automated tests for: 
  - Retrieval correctness (sample queries retrieve expected chunks). 
  - Refusal classifier accuracy. 
  - End‑to‑end response length and citation format.

---

## 13. Limitations & Future Work
* **Source Freshness** – The scraping service runs daily via **GitHub Actions** at 09:15 AM IST; any changes between runs may not be reflected instantly.
* **Language Model Hallucination** – Although RAG reduces hallucination, a small residual risk remains; future work includes stricter grounding with *retrieval‑augmented fine‑tuning*.
* **Multilingual Support** – Currently English‑only; can be extended by adding language‑specific corpora.

---

*Document generated on 2026‑04‑29. All components are designed to comply with the problem‑statement constraints while delivering a fast, factual mutual‑fund FAQ experience.*
