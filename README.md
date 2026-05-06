# Mutual Fund FAQ Assistant (Facts‑Only)

## Overview
A lightweight Retrieval‑Augmented Generation (RAG) based assistant designed to answer factual, objective, and verifiable queries about specific mutual fund schemes. The assistant strictly adheres to a "Facts‑Only" policy, retrieving information exclusively from official public sources.

## Core Features
- **Facts‑Only Q&A**: Answers queries about expense ratios, exit loads, minimum SIP amounts, and more.
- **Source‑Backed**: Every response includes a single, verifiable citation link.
- **Daily Updates**: Automated scraping service runs daily at **9:15 AM** to ensure data freshness.
- **Advisory Refusal**: Automatically refuses queries seeking investment advice or opinions.

## Scope: HDFC Mutual Fund Schemes
This assistant is configured to provide information for the following HDFC schemes:
1. [HDFC Mid-Cap Fund](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
2. [HDFC Equity Fund](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth)
3. [HDFC Focused Fund](https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth)
4. [HDFC ELSS Tax Saver](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth)
5. [HDFC Large Cap Fund](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)

## Disclaimer
> [!IMPORTANT]
> **Facts‑only. No investment advice.**
> This assistant provides only objective data retrieved from official sources. It does not provide opinions, recommendations, or performance comparisons.

## Architecture
The system uses a RAG pipeline. For a detailed technical breakdown, see [Docs/RAG_Architecture.md](Docs/RAG_Architecture.md).

## Setup Instructions

### Prerequisites
- Python 3.9+
- OpenAI API Key (or local LLM environment)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables (create a `.env` file):
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Assistant
To start the scraping service and the UI:
```bash
# Run the UI
streamlit run src/app.py
```

## Known Limitations
- Data freshness is dependent on the daily 9:15 AM crawl.
- Currently supports web‑based data from Groww.in (no PDF parsing in the initial version).
- Refusal handling is based on a keyword/LLM-classifier hybrid and may occasionally trigger on complex factual queries.

---
*Developed for the Milestone‑1 deliverable.*
