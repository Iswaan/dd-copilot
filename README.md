# 🚀 AI Due Diligence Copilot

An enterprise-grade hybrid-RAG (Retrieval-Augmented Generation) pipeline for deep-diving into complex SEC filings, earnings transcripts, and financial documents. Built with FastAPI and Next.js, featuring a stunning glassmorphic UI.

## 📱 Interactive Interface

The Copilot features a beautiful, highly responsive, mobile-first frontend. Below is a real-time demonstration of the end-to-end query flow, showcasing the dynamic sunrise hero background and interactive citation system:

![UI Demonstration](assets/demo.webp)

## 🏗 Architecture & Features

This system is built from the ground up to solve the hardest challenges in financial RAG (hallucinations, loss of context, and source attribution):

- **Hybrid Retrieval (Ensemble)**: Combines dense vector semantic search (BGE-Large via ChromaDB) with sparse keyword search (BM25) to capture both high-level semantic meaning and exact-match financial metrics/acronyms.
- **Cross-Encoder Reranking**: Uses BAAI/bge-reranker-v2-m3 to re-score and perfectly order the top chunks retrieved by the hybrid ensemble before they are passed to the LLM context window.
- **Citation Engine**: Exact source attribution! The generation engine injects UUID markers into its response, which the frontend securely maps into beautifully numbered interactive badges (e.g. [1]). Clicking a badge smoothly scrolls and highlights the exact SEC source chunk card.
- **Pluggable LLM Backend**: Configured to use Groq (llama-3.3-70b-versatile) for blazing-fast inference, but supports Anthropic, OpenAI, or local Ollama.
- **RAGAS Evaluation**: Integrated evaluation pipeline that algorithmically scores Faithfulness, Answer Relevance, Context Precision, and Context Recall using a local llama3 judge to ensure production-quality responses without hallucinations.

## 🛠 Tech Stack

### Frontend (Next.js)
- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS with custom glassmorphic aesthetics
- **Icons & Animation**: Lucide React & Framer Motion
- **Architecture**: Modular component design (ResultsPanel, SourceGrid, AnswerText citation mapper)

### Backend (Python / FastAPI)
- **API**: FastAPI (Uvicorn)
- **Vector Store**: ChromaDB
- **Embeddings & NLP**: sentence-transformers (BGE), ank_bm25
- **LLM Integration**: Groq API, LangChain
- **Evaluation**: RAGAS + local Ollama

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key (or Anthropic/OpenAI)

### Installation

1. **Clone & Setup Environment**
   `ash
   git clone <repo_url>
   cd dd-copilot
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   `

2. **Frontend Setup**
   `ash
   cd frontend
   npm install
   `

3. **Start the Copilot**
   Use the provided development script to launch both the FastAPI backend and Next.js frontend simultaneously:
   `ash
   ./dev.sh
   `
   The UI will be available at http://localhost:3000.

## 🧪 Evaluation

To run the RAGAS evaluation pipeline against your local models:
`ash
python eval/rerun_q14_20.py
`
This incrementally evaluates the system's answers against ground-truth and saves progress to partial_results.json.

---
*Built for absolute confidence in AI-assisted financial diligence.*
