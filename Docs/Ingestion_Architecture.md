# Ingestion Architecture: Chunking & Embedding Pipeline

This document details the processes involved in transforming raw scraped data from Mutual Fund scheme pages into searchable vector embeddings, managed via a CI/CD scheduler.

---

## 1. Pipeline Overview (GitHub Actions Workflow)

The ingestion process is decoupled from the user-facing application and runs on a scheduled GitHub Actions runner.

```mermaid
graph LR
    A[Cron Trigger: 03:45 UTC] --> B[Scraping Action]
    B --> C[Data Extraction]
    C --> D[Chunking Engine]
    D --> E[Embedding Service]
    E --> F[Chroma Cloud Update]
    F --> G[Health Check / Logging]
```

### Schedule Details
- **Trigger**: GitHub Actions `schedule` event.
- **Cron**: `45 3 * * *` (9:15 AM IST).
- **Environment**: Ubuntu-latest runner with Python 3.11 environment.

---

## 2. Chunking Strategy

To ensure high retrieval accuracy for financial facts (Expense Ratios, SIP limits), we employ a **Structure‑Aware Chunking** approach.

### 2.1 Logic & Parameters
- **Strategy**: Recursive Character Text Splitting with semantic boundaries.
- **Chunk Size**: 600 characters (approx. 100‑120 tokens).
- **Chunk Overlap**: 100 characters (preserves context between adjacent sentences/tables).
- **Separators**: `["\n\n", "\n", " ", ""]` — Priority is given to paragraph and line breaks to keep table rows or bullet points together where possible.

### 2.2 Metadata Enrichment
Each chunk is tagged with the following metadata to enable hybrid filtering:
- `fund_name`: e.g., "HDFC Mid‑Cap Fund"
- `source_url`: Original Groww.in link.
- `last_updated`: ISO timestamp of the scrape.
- `chunk_type`: (Header, Table, Paragraph).

---

## 3. Embedding Process

The embedding service converts text chunks into high‑dimensional vectors.

### 3.1 Model Selection
- **Model**: `all‑MiniLM‑L6‑v2` (Sentence Transformers).
- **Dimension**: 384.
- **Rationale**: Extremely fast inference on CPU-based GitHub runners, low memory footprint, and high performance for short factual queries.

### 3.2 Update Mechanism (Upsert)
- **ID Generation**: Hashing the content and fund name to create deterministic IDs (`hash(text + fund_name)`).
- **Deduplication**: If the content hasn't changed since the last scrape, the embedding remains the same, avoiding unnecessary vector DB writes.
- **Batching**: Vectors are processed in batches of 100 to stay within API/Memory limits.

---

## 4. Vector Store Management (Chroma Cloud)

The system is now configured to use a managed **Chroma Cloud** instance, eliminating the need for local database persistence in the repository.

### 4.1 Connection Architecture
- **Client**: `chromadb.HttpClient`
- **Host**: Configured via `CHROMA_CLOUD_HOST` environment variable.
- **Authentication**: Secured using `CHROMA_CLOUD_API_KEY` (Bearer Token).
- **Tenant/Database**: Supports multi-tenant isolation if required by the cloud provider.

### 4.2 Benefits
- **Persistent State**: The vector database is always available and up-to-date, regardless of the GitHub runner's ephemeral nature.
- **Scalability**: Handles large datasets and concurrent queries from multiple users without file-locking issues.
- **Zero Repo Bloat**: No large binary vector files (`data/vector_db/`) are committed to the git history.

---

## 5. Error Handling & Monitoring
- **Validation**: After embedding, a "Test Query" is run against the updated index to ensure retrieval is functioning.
- **Alerting**: If the scraping fails or the embedding error rate exceeds 5%, a GitHub Action failure notification is sent to the dev team.
- **Versioning**: Each daily update creates a snapshot log in the repository to track data evolution.

---
*Last Updated: 2026‑04‑29*
