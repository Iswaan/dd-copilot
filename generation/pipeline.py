import sys
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.hybrid_search import HybridRetriever
from retrieval.rerank import Reranker
from generation.synthesize import generate_answer
from generation.confidence import score_confidence

class DDCopilotPipeline:
    def __init__(self):
        print("Initializing DD-Copilot Pipeline (Retrieval + Rerank + Generation)...")
        self.retriever = HybridRetriever()
        self.reranker = Reranker()
        print("Pipeline ready.\n")
        
    def run(self, query: str) -> dict:
        print(f"Executing query: '{query}'")
        
        # 1. Retrieval
        hybrid_candidates = self.retriever.hybrid_search(query, top_k=20)
        
        # 2. Rerank
        final_candidates = self.reranker.rerank(query, hybrid_candidates, top_n=6)
        
        # 3. Generation
        gen_result = generate_answer(query, final_candidates)
        
        # 4. Confidence Scoring
        cited_chunks = []
        rerank_scores = []
        for cid in gen_result["raw_chunks_used"]:
            for c in final_candidates:
                if c["chunk_id"] == cid:
                    cited_chunks.append(c)
                    rerank_scores.append(c.get("rerank_score", 0.0))
                    break
                    
        confidence = score_confidence(cited_chunks, rerank_scores)
        gen_result["confidence"] = confidence
        
        return gen_result

def print_result(result):
    print("\n" + "="*80)
    print("ANSWER:")
    print("="*80)
    print(result["answer"])
    print("\n" + "="*80)
    print(f"CONFIDENCE: {result['confidence'].upper()}")
    print("="*80)
    print("CITATIONS:")
    if not result["citations"]:
        print("None")
    for i, c in enumerate(result["citations"]):
        print(f"[{c['chunk_id']}] {c['ticker']} {c['filing_type']} - {c['section_heading']}")

def main():
    pipeline = DDCopilotPipeline()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        res = pipeline.run(query)
        print_result(res)
    else:
        queries = [
            "What are the key risk factors for Pfizer based on their most recent 10-K?",
            "What debt obligations does Tesla have coming due?",
            "What is Apple's stock price target for next quarter?"
        ]
        
        for q in queries:
            res = pipeline.run(q)
            print_result(res)
            print("\n")

if __name__ == "__main__":
    main()
