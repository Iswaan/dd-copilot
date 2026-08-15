# AI Due Diligence Copilot

A hybrid Retrieval-Augmented Generation (RAG) platform that ingests SEC filings, financial statements, and investor materials to produce highly accurate, source-backed due diligence answers.

This application is designed to be highly defensible, combining a dense vector database (Chroma DB) with a sparse retrieval index (BM25) and a Cross-Encoder reranker. The generation layer is powered by **Llama-3.3-70b-versatile** via Groq, providing strict inline citations \[chunk_id]\ and an automated confidence score.

## Architecture

The project is built as a modern full-stack web application:
- **Frontend**: React, Next.js, and TailwindCSS (running on port \3000\).
- **Backend**: FastAPI and Python (running on port \8000\).
- **Retrieval Engine**: Hybrid Search (Chroma DB + BM25) with \BAAI/bge-reranker-v2-m3\.
- **Generation Model**: \llama-3.3-70b-versatile\ via Groq.
- **Evaluation Harness**: Local RAGAS evaluation utilizing \llama3\ via Ollama for strict, verifiable performance metrics (Faithfulness, Context Recall, Context Precision, Answer Relevancy).

## Local Development Setup

To run the full stack locally, simply execute the \dev.sh\ script:

\\\ash
# 1. Ensure your virtual environment is active and dependencies are installed
# pip install -r requirements.txt

# 2. Add your Groq API key to a .env file
# GROQ_API_KEY="your-key-here"

# 3. Start the application
bash dev.sh
\\\

The \dev.sh\ script will automatically start:
- **FastAPI Backend** on \http://localhost:8000\
- **Next.js Frontend** on \http://localhost:3000\

Open \http://localhost:3000\ in your browser to interact with the UI.

## Evaluation & Defensibility

We employ the **RAGAS** (Retrieval Augmented Generation Assessment) framework locally via Ollama to rigorously test the pipeline against a curated dataset of SEC-related Q&A pairs.

To run the evaluation:
\\\ash
python eval/run_ragas.py
\\\

Results, including average scores across the dataset, are compiled into \eval/results.md\.

