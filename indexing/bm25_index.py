import os
import json
import string
import pickle
from rank_bm25 import BM25Okapi

def tokenize(text):
    text = text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    return text.split()

def build_bm25():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chunks_file = os.path.join(base_dir, "data", "chunks.jsonl")
    bm25_file = os.path.join(base_dir, "data", "bm25_index.pkl")
    
    print("Loading chunks for BM25...")
    chunks = []
    if not os.path.exists(chunks_file):
        print(f"File not found: {chunks_file}")
        return
        
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
                
    texts = [c["text"] for c in chunks]
    chunk_ids = [c["chunk_id"] for c in chunks]
    
    print("Tokenizing corpus...")
    tokenized_corpus = [tokenize(doc) for doc in texts]
    
    print("Building BM25 index...")
    bm25 = BM25Okapi(tokenized_corpus)
    
    print(f"Saving BM25 index to {bm25_file}...")
    with open(bm25_file, 'wb') as f:
        pickle.dump({"bm25": bm25, "chunk_ids": chunk_ids}, f)
        
    print(f"BM25 index saved successfully. Indexed {len(chunk_ids)} chunks.")

if __name__ == "__main__":
    build_bm25()
