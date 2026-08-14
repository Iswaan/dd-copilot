# dd-copilot

A hybrid RAG platform that ingests SEC filings, financial statements, and investor materials to produce source-backed due diligence answers with citations and confidence scoring

Status: in progress

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   pip install -r requirements.txt
   ```

2. Run the ingestion pipeline:
   ```bash
   python ingestion/download_filings.py
   python ingestion/parse_filings.py
   ```
   
   The parsed files will be saved in `data/parsed/` using the following schema:
   ```json
   {
     "metadata": {"ticker": "...", "filing_type": "...", "date": "...", "source_url": "..."},
     "sections": [{"heading": "...", "text": "..."}],
     "tables": [{"caption": "...", "headers": [], "rows": [[]]}]
   }
   ```

## Architecture

ingestion -> chunking & indexing -> hybrid retrieval -> generation -> evaluation -> UI
