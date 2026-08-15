# 🔍 AI Due Diligence Copilot

<div align="center">
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.103-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Llama_3.3_70B-Groq-f44336?style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/Chroma_DB-Vector_DB-blue?style=for-the-badge" alt="Chroma" />
</div>
<br/>

A **highly defensible**, hybrid Retrieval-Augmented Generation (RAG) platform purpose-built for financial analysts. It ingests massive SEC filings, financial statements, and investor materials to produce highly accurate, source-backed due diligence answers with strict inline citations.

---

## ✨ Key Features

- **Hybrid Retrieval Engine**: Fuses dense vector embeddings (Chroma DB) with sparse keyword matching (BM25) to catch both semantic intent and exact financial metrics.
- **Cross-Encoder Reranking**: Utilizes `BAAI/bge-reranker-v2-m3` to mathematically score and re-order chunks, surfacing only the most highly relevant context.
- **Defensibility-First Generation**: Powered by `Llama-3.3-70b-versatile` via Groq. Every claim is strictly backed by inline `[chunk_id]` citations linked directly to the source text.
- **Automated Confidence Scoring**: The pipeline evaluates its own retrieved context and assigns a deterministic confidence tier (High, Medium, Low) to prevent hallucinations.
- **Rigorous Evaluation Harness**: Integrates the **RAGAS** framework running via a local `llama3` judge to continuously score Faithfulness, Context Recall, Context Precision, and Answer Relevancy.
- **Modern Full-Stack UI**: A sleek, reactive Next.js frontend built with TailwindCSS, seamlessly communicating with a high-performance Python FastAPI backend.

---

## 🏗️ Architecture Flow

1. **Ingestion & Indexing**: Raw SEC filings are chunked and embedded via `SentenceTransformers`. The embeddings are stored in Chroma DB, while exact text is indexed via BM25.
2. **Query Routing**: The user inputs a query via the Next.js frontend, which POSTs to the FastAPI `/query` endpoint.
3. **Hybrid Search**: The backend runs parallel vector and sparse searches to retrieve the top 20 candidate chunks.
4. **Reranking**: The BGE Cross-Encoder reranks the 20 candidates down to the definitive top 6 chunks.
5. **Synthesis**: Groq generates a structured response (Summary, Key Findings, Caveats) strictly constrained to the top 6 chunks.
6. **Delivery**: The payload, including source cards, citations, and confidence scores, is rendered in the UI.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A valid [Groq API Key](https://console.groq.com/)

### 1. Installation

Clone the repository and install dependencies for both the backend and frontend:

```bash
# Backend Dependencies
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend Dependencies
cd frontend
npm install
cd ..
```

### 2. Configuration

Create a `.env` file in the root directory and add your API keys:

```env
GROQ_API_KEY="gsk_your_api_key_here"
# Optional fallback models
OPENROUTER_API_KEY="sk-or-v1-..." 
```

### 3. Run the Stack

We provide an orchestration script to spin up the entire application concurrently.

```bash
bash dev.sh
```

- The **FastAPI Backend** will launch on `http://localhost:8000`
- The **Next.js Frontend** will launch on `http://localhost:3000`

Navigate to `http://localhost:3000` to start running due diligence queries!

---

## 🧪 Evaluation & Defensibility

We employ the **RAGAS** (Retrieval Augmented Generation Assessment) framework locally via Ollama to rigorously test the pipeline against a curated dataset of SEC-related Q&A pairs without leaking data or burning API credits.

To execute the evaluation suite:
```bash
python eval/run_ragas.py
```

The script automatically tests the pipeline against the dataset and compiles the metric averages (Faithfulness, Relevancy, Precision, Recall) into `eval/results.md`.

---

## 📁 Repository Structure

```text
dd-copilot/
├── backend/          # FastAPI entry points and API routers
├── data/             # Raw SEC filings, parsed chunks, and Chroma DB storage
├── eval/             # RAGAS evaluation harness, datasets, and result outputs
├── frontend/         # Next.js React application and UI components
├── generation/       # LLM generation logic, prompts, and confidence scoring
├── tests/            # Pytest suite for retrieval and generation validation
├── README.md
├── dev.sh            # Local startup script
└── requirements.txt  # Python backend dependencies
```
