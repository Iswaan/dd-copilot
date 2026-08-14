import sys
import os

# Add project root to python path so we can import from retrieval
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.hybrid_search import HybridRetriever
from retrieval.rerank import Reranker

def print_result(rank, chunk):
    meta = chunk["metadata"]
    score = chunk.get("rerank_score", 0.0)
    rrf = chunk.get("rrf_score", 0.0)
    ticker = meta.get("ticker", "UNKNOWN")
    f_type = meta.get("filing_type", "UNKNOWN")
    date = meta.get("date", "UNKNOWN")
    c_type = meta.get("chunk_type", "UNKNOWN").upper()
    section = meta.get("section_heading", "None")
    
    # Format text preview
    text = chunk["text"].replace('\n', ' ')
    preview = text[:200] + "..." if len(text) > 200 else text
    
    print(f"\n[Rank {rank} | Rerank Score: {score:.4f} | RRF: {rrf:.4f}] {ticker} {f_type} ({date}) - {c_type}")
    print(f"Section: {section}")
    print(f"Preview: {preview}")

def run_test_queries(retriever, reranker, queries):
    for query in queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        print("Running Hybrid Search (Top 20)...")
        hybrid_candidates = retriever.hybrid_search(query, top_k=20)
        
        print("Running Cross-Encoder Reranking (Top 6)...")
        final_results = reranker.rerank(query, hybrid_candidates, top_n=6)
        
        for i, res in enumerate(final_results):
            print_result(i+1, res)

def main():
    retriever = HybridRetriever()
    reranker = Reranker()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_test_queries(retriever, reranker, [query])
    else:
        queries = [
            "What are Apple's main supply chain risks mentioned in recent filings?",
            "Compare revenue growth trends across the tracked companies",
            "What debt obligations does Tesla have coming due?"
        ]
        run_test_queries(retriever, reranker, queries)

if __name__ == "__main__":
    main()
