import os
import json
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_filings():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parsed_dir = os.path.join(base_dir, "data", "parsed")
    chunks_file = os.path.join(base_dir, "data", "chunks.jsonl")
    
    # Tiktoken-based text splitter for 400-600 token chunks (target ~500) with 50 overlap
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-3.5-turbo",
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    all_chunks = []
    text_chunks_count = 0
    table_chunks_count = 0
    
    for filename in os.listdir(parsed_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(parsed_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        metadata = data.get("metadata", {})
        ticker = metadata.get("ticker", "")
        filing_type = metadata.get("filing_type", "")
        date = metadata.get("date", "")
        source_url = metadata.get("source_url", "")
        
        # Process narrative sections
        for section in data.get("sections", []):
            heading = section.get("heading", "")
            text = section.get("text", "")
            if not text.strip():
                continue
                
            splits = text_splitter.split_text(text)
            for split in splits:
                chunk_id = str(uuid.uuid4())
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "text": split,
                    "metadata": {
                        "ticker": ticker,
                        "filing_type": filing_type,
                        "date": date,
                        "source_url": source_url,
                        "section_heading": heading,
                        "chunk_type": "text"
                    }
                })
                text_chunks_count += 1
                
        # Process tables
        for table in data.get("tables", []):
            caption = table.get("caption", "")
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            
            table_text = f"Caption: {caption}\n"
            if headers:
                table_text += " | ".join(headers) + "\n"
            for row in rows:
                table_text += " | ".join(row) + "\n"
                
            chunk_id = str(uuid.uuid4())
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": table_text,
                "metadata": {
                    "ticker": ticker,
                    "filing_type": filing_type,
                    "date": date,
                    "source_url": source_url,
                    "section_heading": caption,
                    "chunk_type": "table",
                    "table_data": json.dumps({"headers": headers, "rows": rows})
                }
            })
            table_chunks_count += 1
            
    with open(chunks_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
            
    print(f"Produced {len(all_chunks)} chunks.")
    print(f"Text chunks: {text_chunks_count}")
    print(f"Table chunks: {table_chunks_count}")

if __name__ == "__main__":
    chunk_filings()
