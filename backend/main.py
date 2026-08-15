from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import the pipeline
from generation.pipeline import DDCopilotPipeline

app = FastAPI(title="AI Due Diligence Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting up FastAPI and loading models...")
pipeline = DDCopilotPipeline()
print("Models loaded successfully.")

class QueryRequest(BaseModel):
    question: str
    ticker: Optional[str] = None

class Citation(BaseModel):
    chunk_id: str
    ticker: str
    filing_type: str
    section_heading: str
    source_url: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tickers")
def get_tickers():
    return {"tickers": ["AAPL", "MSFT", "TSLA", "PFE", "JPM"]}

@app.post("/query", response_model=QueryResponse)
def post_query(req: QueryRequest):
    try:
        hybrid_candidates = pipeline.retriever.hybrid_search(
            req.question, 
            top_k=20, 
            ticker_filter=req.ticker if req.ticker and req.ticker != "multi" else None
        )
        
        final_candidates = pipeline.reranker.rerank(req.question, hybrid_candidates, top_n=6)
        
        from generation.synthesize import generate_answer
        from generation.confidence import score_confidence
        
        gen_result = generate_answer(req.question, final_candidates)
        
        cited_chunks = []
        rerank_scores = []
        for cid in gen_result.get("raw_chunks_used", []):
            for c in final_candidates:
                if c["chunk_id"] == cid:
                    cited_chunks.append(c)
                    rerank_scores.append(c.get("rerank_score", 0.0))
                    break
                    
        confidence = score_confidence(cited_chunks, rerank_scores)
        
        citations = []
        for c in gen_result.get("citations", []):
            citations.append(Citation(
                chunk_id=c.get("chunk_id", ""),
                ticker=c.get("ticker", ""),
                filing_type=c.get("filing_type", ""),
                section_heading=c.get("section_heading", ""),
                source_url=c.get("source_url", "")
            ))
            
        return QueryResponse(
            answer=gen_result.get("answer", ""),
            citations=citations,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
