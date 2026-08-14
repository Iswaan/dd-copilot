import os
import json
import pickle
import chromadb
from rank_bm25 import BM25Okapi
import string
import numpy as np
from sentence_transformers import SentenceTransformer

class HybridRetriever:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.chroma_dir = os.path.join(self.base_dir, "data", "chroma_db")
        self.bm25_file = os.path.join(self.base_dir, "data", "bm25_index.pkl")
        self.chunks_file = os.path.join(self.base_dir, "data", "chunks.jsonl")
        
        print("Loading Chroma DB...")
        self.client = chromadb.PersistentClient(path=self.chroma_dir)
        self.collection = self.client.get_collection(name="dd_filings")
        
        print("Loading SentenceTransformer model...")
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5", device=device)
        
        print("Loading BM25 index...")
        with open(self.bm25_file, 'rb') as f:
            bm25_data = pickle.load(f)
            self.bm25 = bm25_data["bm25"]
            self.bm25_chunk_ids = bm25_data["chunk_ids"]
            
        print("Loading chunks mapping...")
        self.chunks_dict = {}
        with open(self.chunks_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    c = json.loads(line)
                    self.chunks_dict[c["chunk_id"]] = c
        print("HybridRetriever initialized successfully.\n")

    def _tokenize(self, text):
        text = text.lower()
        for p in string.punctuation:
            text = text.replace(p, ' ')
        return text.split()

    def hybrid_search(self, query: str, top_k: int = 20, ticker_filter: str = None) -> list:
        """
        Run dense and sparse search, fuse with RRF, and return top_k chunks.
        """
        # 1. Dense Search
        query_embedding = self.embed_model.encode(query, show_progress_bar=False).tolist()
        where_clause = {"ticker": ticker_filter} if ticker_filter else None
        
        # Query Chroma (fetch more for better RRF fusion overlap)
        fetch_k = top_k * 2
        dense_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_k,
            where=where_clause,
            include=["metadatas"]
        )
        
        dense_hits = []
        if dense_results["ids"] and dense_results["ids"][0]:
            for rank, cid in enumerate(dense_results["ids"][0]):
                dense_hits.append({
                    "chunk_id": cid,
                    "rank": rank + 1
                })
                
        # 2. Sparse Search (BM25)
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top indices from BM25
        top_n_idx = np.argsort(bm25_scores)[::-1]
        
        sparse_hits = []
        rank = 1
        for idx in top_n_idx:
            cid = self.bm25_chunk_ids[idx]
            chunk = self.chunks_dict[cid]
            if ticker_filter and chunk["metadata"]["ticker"] != ticker_filter:
                continue
            
            # Skip if zero score
            if bm25_scores[idx] <= 0:
                break
                
            sparse_hits.append({
                "chunk_id": cid,
                "rank": rank
            })
            rank += 1
            if len(sparse_hits) >= fetch_k:
                break
                
        # 3. Reciprocal Rank Fusion (RRF)
        k = 60
        rrf_scores = {}
        for hit in dense_hits:
            cid = hit["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + hit["rank"])
            
        for hit in sparse_hits:
            cid = hit["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + hit["rank"])
            
        # Sort by RRF score
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Construct final results
        final_results = []
        for cid, score in sorted_rrf:
            chunk = self.chunks_dict[cid]
            chunk_copy = dict(chunk)
            chunk_copy["rrf_score"] = score
            final_results.append(chunk_copy)
            
        return final_results

# Example direct usage
def hybrid_search(query: str, top_k: int = 20, ticker_filter: str = None):
    retriever = HybridRetriever()
    return retriever.hybrid_search(query, top_k, ticker_filter)
