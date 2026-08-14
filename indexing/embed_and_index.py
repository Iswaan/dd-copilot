import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def run_indexing():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chunks_file = os.path.join(base_dir, "data", "chunks.jsonl")
    chroma_dir = os.path.join(base_dir, "data", "chroma_db")
    
    print("Loading chunks...")
    chunks = []
    if not os.path.exists(chunks_file):
        print(f"File not found: {chunks_file}")
        return
        
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
                
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    
    print("Loading embedding model BAAI/bge-large-en-v1.5...")
    model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cuda")
    
    print(f"Embedding {len(texts)} chunks...")
    batch_size = 32
    # encode handles the batching and progress bar natively
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    embeddings = embeddings.tolist()
    
    print("Storing vectors in ChromaDB...")
    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_or_create_collection(name="dd_filings")
    
    insert_batch = 5000
    for i in tqdm(range(0, len(ids), insert_batch), desc="Inserting into Chroma"):
        collection.add(
            ids=ids[i:i+insert_batch],
            embeddings=embeddings[i:i+insert_batch],
            metadatas=metadatas[i:i+insert_batch],
            documents=texts[i:i+insert_batch]
        )
        
    print(f"Chroma collection 'dd_filings' now contains {collection.count()} chunks.")

if __name__ == "__main__":
    run_indexing()
