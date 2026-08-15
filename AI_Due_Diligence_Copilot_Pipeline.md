# AI Due Diligence Copilot — Full Build Pipeline

A RAG platform that ingests company filings, financial statements, investor
presentations, and market reports, and produces source-backed risk
assessments, growth-opportunity summaries, and executive summaries.

This doc is written to be handed to Antigravity phase-by-phase, the same way
you've been running CASCADE2VEC. Each phase has: goal, what gets built, and a
ready-to-paste Antigravity prompt. Don't skip ahead — each phase assumes the
previous one's artifacts exist.

---

## Architecture overview

```
SEC EDGAR filings (10-K/10-Q/8-K, PDFs)
        |
        v
[Ingestion & Parsing]  -- table-aware chunking, section detection
        |
        v
[Embedding + Indexing] -- dense (vector DB) + sparse (BM25) indexes
        |
        v
[Hybrid Retrieval]     -- BM25 + dense fusion, cross-encoder re-rank
        |
        v
[Generation Layer]     -- LLM synthesis with inline citations
        |
        v
[Evaluation Harness]   -- RAGAS: faithfulness, answer relevancy, citation accuracy
        |
        v
[UI]                   -- Streamlit or minimal React front end
```

Stack recommendation (all free/open-source, resume-friendly, no vendor lock-in):
- **Parsing**: `unstructured` or PyMuPDF for PDFs, `edgartools`/`sec-edgar-downloader` for filings
- **Chunking**: semantic + table-aware (tables kept intact, never split mid-row)
- **Embeddings**: `sentence-transformers` (e.g. `bge-large-en-v1.5`) — free, local, no API cost
- **Vector DB**: Chroma or Qdrant (both run locally, easy to demo)
- **Sparse retrieval**: `rank_bm25` or Elasticsearch if you want to look more "production"
- **Re-ranker**: `bge-reranker-v2-m3` cross-encoder
- **Generation**: Claude API or a local model (Llama 3.1 8B via Ollama) — pick Claude API if you want citation-quality generation without a big GPU
- **Eval**: RAGAS framework
- **UI**: Streamlit (fast) — skip React unless you want extra polish for the resume

---

## Phase 1 — Project scaffold & data ingestion

**Goal:** Set up repo structure, pull real filings from SEC EDGAR, get raw
text + tables extracted and saved to disk.

**Deliverables:**
- Repo skeleton (`/ingestion`, `/indexing`, `/retrieval`, `/generation`, `/eval`, `/ui`, `/data`)
- A script that downloads 10-K/10-Q filings for a configurable list of tickers
- A parser that extracts clean text sections + tables (as structured JSON, not flattened text) from each filing
- Output: `/data/parsed/{ticker}_{filing_type}_{date}.json` with fields: `sections: [{heading, text}]`, `tables: [{caption, rows}]`, `metadata: {ticker, filing_type, date, source_url}`

**Antigravity prompt — Phase 1:**
```
Set up a new Python project called "dd-copilot" with this structure:

dd-copilot/
  ingestion/
    download_filings.py
    parse_filings.py
  indexing/
  retrieval/
  generation/
  eval/
  ui/
  data/
    raw/
    parsed/
  requirements.txt
  README.md

Requirements:
1. download_filings.py: use the `sec-edgar-downloader` package to download
   10-K and 10-Q filings for a configurable list of tickers (start with
   ["AAPL", "MSFT", "TSLA", "JPM", "PFE"] as a default list, 3 filings per
   ticker). Save raw filings to data/raw/{ticker}/.

2. parse_filings.py: parse each raw filing (HTML or PDF) into structured
   JSON. Use the `unstructured` library's partition functions to separate
   narrative text sections from tables. Do NOT flatten tables into plain
   text — preserve them as structured objects with rows and columns intact,
   since due diligence tables (balance sheets, income statements) lose all
   meaning if split across chunks or turned into prose.

   Output format per filing, saved to data/parsed/{ticker}_{filing_type}_{date}.json:
   {
     "metadata": {"ticker": str, "filing_type": str, "date": str, "source_url": str},
     "sections": [{"heading": str, "text": str}],
     "tables": [{"caption": str, "headers": list, "rows": list of lists}]
   }

3. Add a requirements.txt with: sec-edgar-downloader, unstructured[pdf],
   pandas, python-dotenv

4. Add a README.md explaining what the project does, how to run
   download_filings.py then parse_filings.py, and the JSON schema above.

5. Add basic error handling: if a filing fails to parse, log the ticker and
   filing type to a data/parsed/failed.log instead of crashing the whole run.

After building this, run download_filings.py and parse_filings.py end to
end on the default ticker list and show me the output for one parsed filing
so I can verify the JSON structure looks right before we move to indexing.
```

---

## Phase 2 — Chunking & embedding

**Goal:** Turn parsed JSON into retrieval-ready chunks, embed them, and
build both a dense vector index and a sparse BM25 index.

**Deliverables:**
- `indexing/chunk.py`: chunks narrative sections (semantic chunking, ~400-600 tokens, with overlap) and keeps each table as one atomic chunk with its caption prepended
- `indexing/embed_and_index.py`: embeds chunks with `bge-large-en-v1.5`, stores in Chroma with metadata (ticker, filing_type, date, section heading, chunk_type: "text"|"table")
- `indexing/bm25_index.py`: builds a parallel BM25 index over the same chunks for hybrid retrieval later

**Antigravity prompt — Phase 2:**
```
Building on the dd-copilot project from Phase 1 (data/parsed/*.json exists
with sections and tables), implement chunking and indexing:

1. indexing/chunk.py:
   - For each parsed filing JSON, chunk narrative "sections" text into
     ~400-600 token chunks with ~50 token overlap, using a sentence-aware
     splitter (don't cut mid-sentence).
   - For "tables", treat each table as ONE atomic chunk. Prepend the table's
     caption and the filing's section context to the chunk text so it's
     retrievable on its own, then also keep the structured rows/headers as
     metadata (not flattened into the text) for potential downstream
     structured queries.
   - Every chunk must carry metadata: ticker, filing_type, date, source_url,
     section_heading, chunk_type ("text" or "table"), and a unique chunk_id.
   - Save all chunks to data/chunks.jsonl (one JSON object per line).

2. indexing/embed_and_index.py:
   - Load sentence-transformers model "BAAI/bge-large-en-v1.5".
   - Embed every chunk from data/chunks.jsonl.
   - Store embeddings + metadata in a local Chroma collection called
     "dd_filings", persisted to disk at data/chroma_db/.
   - Batch the embedding calls (batch size 32) and show a progress bar.

3. indexing/bm25_index.py:
   - Build a BM25 index (using rank_bm25) over the same chunks, tokenized
     with simple lowercase + punctuation stripping.
   - Persist it to disk (pickle is fine) at data/bm25_index.pkl, along with
     a parallel list mapping BM25 doc position -> chunk_id, so we can look
     up full chunk data after a BM25 hit.

4. Add these three scripts to requirements.txt as needed
   (sentence-transformers, chromadb, rank_bm25).

Run the full chunking + indexing pipeline end to end and report: total
number of chunks produced, how many are "table" type vs "text" type, and
confirm both the Chroma collection and BM25 index were written to disk
successfully.
```

---

## Phase 3 — Hybrid retrieval + re-ranking

**Goal:** Given a query, retrieve from both indexes, fuse results, and
re-rank with a cross-encoder for precision.

**Deliverables:**
- `retrieval/hybrid_search.py`: runs dense (Chroma) + sparse (BM25) search in parallel, fuses with Reciprocal Rank Fusion (RRF)
- `retrieval/rerank.py`: re-ranks the fused top-K (e.g. top 20) with `bge-reranker-v2-m3` cross-encoder down to a final top-N (e.g. top 6)
- A CLI test script so you can sanity-check retrieval quality before wiring up generation

**Antigravity prompt — Phase 3:**
```
Building on dd-copilot Phase 2 (Chroma collection "dd_filings" and BM25
index at data/bm25_index.pkl both exist), implement hybrid retrieval:

1. retrieval/hybrid_search.py:
   - Function hybrid_search(query: str, top_k: int = 20, ticker_filter:
     str = None) -> list of chunk dicts.
   - Run dense search against the Chroma "dd_filings" collection (top 20)
     and sparse BM25 search (top 20) in parallel.
   - Fuse the two ranked lists using Reciprocal Rank Fusion (RRF, k=60 as
     the standard constant).
   - If ticker_filter is provided, restrict results to that ticker's
     metadata before fusion.
   - Return the fused top_k chunks with their metadata and fusion score.

2. retrieval/rerank.py:
   - Load cross-encoder model "BAAI/bge-reranker-v2-m3".
   - Function rerank(query: str, candidates: list of chunk dicts, top_n:
     int = 6) -> list of chunk dicts, sorted by cross-encoder relevance
     score, truncated to top_n.

3. retrieval/test_retrieval.py:
   - A simple CLI script: takes a query string as input, runs
     hybrid_search() then rerank(), and prints each final chunk's ticker,
     filing_type, section_heading, chunk_type, and a 200-character preview
     of its text, along with its rerank score.

Test it with these three queries and show me the output for each so I can
judge retrieval quality before we build generation:
  - "What are Apple's main supply chain risks mentioned in recent filings?"
  - "Compare revenue growth trends across the tracked companies"
  - "What debt obligations does Tesla have coming due?"
```

---

## Phase 4 — Generation with citations

**Goal:** Take retrieved chunks + a user question, and generate a grounded
answer with inline source citations, plus a confidence signal.

**Deliverables:**
- `generation/synthesize.py`: builds a strict system prompt that forces the
  model to cite chunk_ids inline and refuse to answer beyond what's in the
  retrieved context
- `generation/confidence.py`: a lightweight confidence score based on (a)
  re-ranker scores of the chunks used, (b) whether the generated claims can
  be traced back to specific chunks
- Output format: structured JSON with `answer`, `citations: [{chunk_id,
  ticker, filing_type, source_url}]`, `confidence: "high"|"medium"|"low"`

**Antigravity prompt — Phase 4:**
```
Building on dd-copilot Phase 3 (hybrid_search + rerank working), implement
the generation layer:

1. generation/synthesize.py:
   - Function generate_answer(query: str, chunks: list of chunk dicts) ->
     dict.
   - Use the Anthropic API (model "claude-sonnet-4-6") to synthesize an
     answer. Build a system prompt that:
     a) Instructs the model to answer ONLY using the provided chunks, and
        explicitly say "The filings don't contain enough information to
        answer this" if the chunks don't support an answer.
     b) Requires every factual claim to be followed by an inline citation
        marker like [chunk_id] pointing to the specific chunk it came from.
     c) For due-diligence-style questions, structure the answer as: Summary
        (2-3 sentences), Key Findings (bulleted, each with a citation),
        Risks/Caveats (if applicable).
   - Parse the model's response to extract which chunk_ids were actually
     cited, and return:
     {
       "answer": str (with inline [chunk_id] markers),
       "citations": [{"chunk_id": str, "ticker": str, "filing_type": str,
                       "source_url": str, "section_heading": str}],
       "raw_chunks_used": list of chunk_ids
     }

2. generation/confidence.py:
   - Function score_confidence(chunks_used: list of chunk dicts,
     rerank_scores: list of float) -> str ("high"|"medium"|"low").
   - Simple heuristic to start: if average rerank score of cited chunks >
     0.7 and at least 2 distinct chunks were cited -> "high"; if average
     score > 0.4 -> "medium"; else "low". Add a comment noting this is a
     v1 heuristic and could be replaced with a learned model later.

3. generation/pipeline.py:
   - Wire it together: query -> hybrid_search -> rerank -> generate_answer
     -> score_confidence -> return final combined dict.
   - Add a CLI entry point so I can run: python pipeline.py "your question
     here" and see the full structured output printed nicely.

Test with: "What are the key risk factors for Pfizer based on their most
recent 10-K?" and show me the full output including citations and
confidence score.
```

---

## Phase 5 — Evaluation harness

**Goal:** Get real, reportable numbers for your resume/README — this is
what separates a "toy RAG demo" from something you can defend in an
interview.

**Deliverables:**
- A small labeled eval set (15-25 question/answer pairs you write by hand
  from the filings, with ground-truth source chunks)
- `eval/run_ragas.py`: runs RAGAS metrics — faithfulness, answer relevancy,
  context precision, context recall
- `eval/results.md`: auto-generated table of scores

**Antigravity prompt — Phase 5:**
```
Building on dd-copilot Phase 4 (generation pipeline working end to end),
implement an evaluation harness:

1. eval/eval_set.json:
   - Create a template file with 20 entries, each:
     {"question": str, "ground_truth_answer": str, "ground_truth_ticker":
     str}
   - Pre-fill 5 example entries based on realistic due-diligence questions
     (risk factors, revenue trends, debt, litigation, competitive
     positioning) so I can see the format, then leave 15 as empty
     templates for me to fill in by hand from the actual filings.

2. eval/run_ragas.py:
   - For each entry in eval_set.json (only ones with ground_truth_answer
     filled in), run it through pipeline.py's full flow to get the
     generated answer and retrieved contexts.
   - Use the `ragas` library to compute: faithfulness, answer_relevancy,
     context_precision, context_recall for each question.
   - Aggregate into an overall average per metric.
   - Save per-question and aggregate results to eval/results.json and a
     human-readable eval/results.md table.

3. Add `ragas` and `datasets` to requirements.txt.

Do NOT run this yet since the eval_set.json ground truths aren't filled in.
Just build the harness and confirm it runs cleanly against the 5 pre-filled
example questions, and show me those 5 results so I can check the metrics
look sane before I fill in the rest by hand.
```

*(This is the one phase where you do real manual work — writing 15-20
good eval questions with ground-truth answers. That's expected and it's
what makes the eval numbers legitimate rather than fabricated. Budget an
evening for this.)*

---

## Phase 6 — Full-stack modern web UI (backend + frontend together)

**Goal:** One cool, modern, dynamic web app — FastAPI backend + a
React/Vite/Tailwind/Framer Motion frontend, built together in the same
repo, in a single Antigravity pass. No separate tool needed.

**Deliverables:**
- `backend/main.py`: FastAPI app wrapping `pipeline.py` (`/query`,
  `/tickers`, `/health`)
- `frontend/`: a Vite + React + TypeScript + Tailwind app with Framer
  Motion animations, dark fintech-style design
- A root `dev.sh` (or `Makefile`) to run both together locally
- Deployable later to Railway/Render (backend) + Vercel (frontend), but
  fully working locally first

**Antigravity prompt — Phase 6:**
```
Building on dd-copilot Phase 5 (generation/pipeline.py works end to end),
build a full-stack web app: a FastAPI backend and a modern React frontend,
in the same repo.

PART A — Backend (backend/main.py):

1. FastAPI app exposing:

   a) POST /query
      Request: {"question": str, "ticker": str | null}
      Response:
      {
        "answer": str,
        "citations": [
          {"chunk_id": str, "ticker": str, "filing_type": str,
           "section_heading": str, "source_url": str}
        ],
        "confidence": "high" | "medium" | "low"
      }
      Calls the existing pipeline.py function directly (import it, don't
      shell out). If ticker is provided, pass it as ticker_filter to
      hybrid_search.

   b) GET /tickers -> {"tickers": [str, ...]}, the distinct tickers found
      in data/chunks.jsonl, for the frontend's filter dropdown.

   c) GET /health -> {"status": "ok"}

2. Use Pydantic models for request/response validation so /docs renders a
   clean OpenAPI schema. Enable CORS for all origins during local dev
   (add a TODO to lock this down before any public deployment). Handle
   pipeline errors gracefully — return 500 with {"error": str}, log the
   traceback server-side, never crash the process.

3. backend/requirements.txt: fastapi, uvicorn, pydantic.

PART B — Frontend (frontend/, Vite + React + TypeScript + Tailwind + Framer Motion):

Design direction: a dark, professional fintech aesthetic — think Bloomberg
terminal meets a clean modern SaaS product, NOT a generic centered-card
AI-chatbot template. Deep charcoal/navy background, one sharp accent color
(electric blue or emerald), strong typographic hierarchy, real motion
(smooth entrance transitions, a subtle reveal animation on the answer
text, hover-lift on cards, a glowing/pulsing confidence badge). Fully
responsive down to mobile width.

Layout (single page):
1. Header: product name + short tagline ("Source-backed due diligence in
   seconds"), plus a small "portfolio project — not investment advice"
   badge.

2. Query panel:
   - Ticker filter dropdown, populated on load via GET /tickers.
   - Large question input, with 4-5 clickable example-question chips that
     pre-fill it (e.g. "What are Apple's supply chain risks?", "Compare
     revenue growth trends across tracked companies").
   - "Run Due Diligence" button with an animated loading state while
     awaiting the API response.

3. Results panel (animates in after POST /query resolves):
   - Answer text with inline citation markers rendered as small clickable
     numbered badges (not raw [chunk_id] text) — clicking one scrolls to
     and highlights the matching source card.
   - Confidence indicator as a colored pill (green/amber/red for
     high/medium/low) with a subtle glow matching its color.
   - "Sources" section as a card grid below, one card per citation:
     ticker, filing type, section heading, link icon to source_url.
     Hover-lift effect on each card.

4. Explicit loading, empty, and error states — no blank screens, no raw
   error dumps.

Wire the frontend to call http://localhost:8000 in dev (define this as a
single config constant, easy to swap for a deployed URL later).

PART C — Glue:
1. Add a root-level dev.sh script that starts the backend
   (uvicorn backend.main:app --reload --port 8000) and frontend
   (cd frontend && npm run dev) together, e.g. using concurrently or two
   backgrounded processes with clear log prefixes.
2. Update the README with setup + run instructions for both parts.

Run both servers, confirm the frontend successfully calls /tickers and
/query end to end with a real question, and describe what the UI looks
like so I can sanity check it before I take screenshots for my portfolio.
```

---

## What to put on your resume/CV

Once built, a one-line bullet like this fits your existing CV style
(metrics-driven, no fluff):

> **AI Due Diligence Copilot** — Built a hybrid RAG system over SEC filings (10-K/10-Q) combining dense + BM25 retrieval with cross-encoder re-ranking and citation-grounded generation; achieved [X]% faithfulness and [Y]% context precision on a 20-question evaluation set (RAGAS), reducing manual filing review time for sample due-diligence questions from ~15 min to <30 sec.

Fill in the X/Y once Phase 5 gives you real numbers — don't estimate them.
Following your standing CV rule, this goes in as a **project entry with no
dates**.

---

## Sequencing note

Run these phases in order, one Antigravity prompt at a time, and eyeball
the output before moving to the next phase — same workflow you use for
CASCADE2VEC. Phase 5 (eval) is the one that actually makes this resume
project defensible in an interview, so don't skip it or rush it. Phase 6
builds the entire full-stack UI (backend + frontend) in one pass — once
it's confirmed working locally, deploy the backend to Railway/Render and
the frontend to Vercel for a live, sharable link.
