import torch
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        print("Loading CrossEncoder model BAAI/bge-reranker-v2-m3...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Download and load the cross encoder model
        self.model = CrossEncoder("BAAI/bge-reranker-v2-m3", device=device)
        print(f"Reranker initialized on {device}.\n")
        
    def rerank(self, query: str, candidates: list, top_n: int = 6) -> list:
        """
        Rerank a list of chunk candidates using cross-encoder scores.
        """
        if not candidates:
            return []
            
        pairs = [[query, c["text"]] for c in candidates]
        
        # Calculate cross-encoder scores
        scores = self.model.predict(pairs, show_progress_bar=False)
        
        # Update chunks with rerank scores
        for i, c in enumerate(candidates):
            c["rerank_score"] = float(scores[i])
            
        # Sort chunks by cross-encoder score
        sorted_candidates = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        
        # Return top N
        return sorted_candidates[:top_n]

def rerank(query: str, candidates: list, top_n: int = 6):
    reranker = Reranker()
    return reranker.rerank(query, candidates, top_n)
