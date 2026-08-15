import os
import json
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import langchain_community.chat_models
import langchain_google_vertexai
sys.modules['langchain_community.chat_models.vertexai'] = type('vertexai', (), {'ChatVertexAI': langchain_google_vertexai.ChatVertexAI})

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from retrieval.hybrid_search import HybridRetriever
from retrieval.rerank import rerank
from generation.synthesize import generate_answer
from datasets import Dataset
from ragas import evaluate, RunConfig
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_ollama import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

class SentenceTransformerWrapper:
    def __init__(self, model):
        self._model_instance = model
        self.model = "BAAI/bge-large-en-v1.5"
    def embed_documents(self, texts):
        return self._model_instance.encode(texts, normalize_embeddings=True).tolist()
    def embed_query(self, text):
        return self._model_instance.encode([text], normalize_embeddings=True)[0].tolist()

def main():
    print("Loading eval set...")
    with open("eval/eval_set.json", "r", encoding="utf-8") as f:
        full_set = json.load(f)
        
    eval_items = [item for item in full_set if item.get("question") and item.get("ground_truth_answer")]
    
    # Isolate Q14-20 (indices 13 to 19)
    q14_20_items = eval_items[13:20]
    print(f"Processing {len(q14_20_items)} items (Q14-20)...")
    
    retriever = HybridRetriever()
    
    results_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
        "reference": []
    }
    
    succeeded_indices = []
    failed_indices = []
    
    print("Generating answers for Q14-20...")
    for idx, item in enumerate(q14_20_items):
        q_idx = 14 + idx
        q = item["question"]
        print(f"\\nProcessing Q{q_idx}: {q}")
        
        ticker = item.get("ground_truth_ticker")
        if ticker and ticker != "multi":
            candidates = retriever.hybrid_search(q, top_k=20, ticker_filter=ticker)
        else:
            candidates = retriever.hybrid_search(q, top_k=20)
            
        top_chunks = rerank(q, candidates, top_n=6)
        
        try:
            gen_result = generate_answer(q, top_chunks)
            
            # The original pipeline might just return a string starting with 'Groq API Error' if max_retries hit
            if "Groq API Error" in gen_result["answer"]:
                raise Exception(gen_result["answer"])
                
        except Exception as e:
            failed_indices.append(q_idx)
            print(f"\\n[!] Generation failed at Q{q_idx} with error: {e}")
            print(f"Succeeded Qs: {succeeded_indices}")
            print(f"Failed Qs: {failed_indices}")
            print("Aborting immediately to prevent merging partial data.")
            sys.exit(1)
            
        results_data["question"].append(q)
        results_data["answer"].append(gen_result["answer"])
        results_data["contexts"].append([c["text"] for c in top_chunks])
        results_data["ground_truth"].append(item["ground_truth_answer"])
        results_data["reference"].append(item["ground_truth_answer"])
        succeeded_indices.append(q_idx)
        
    print(f"\\nAll 7 generation steps completed successfully! Succeeded Qs: {succeeded_indices}")
    
    dataset = Dataset.from_dict(results_data)
    
    print("\\nSetting up RAGAS judges (Local Ollama llama3:latest)...")
    llm = ChatOllama(model="llama3:latest", base_url="http://localhost:11434", temperature=0.0)
    ragas_llm = LangchainLLMWrapper(llm)
    
    embeddings_wrapper = SentenceTransformerWrapper(retriever.embed_model)
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings_wrapper)
    
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    
    print("Running RAGAS evaluation for Q14-20...")
    run_config = RunConfig(timeout=300, max_workers=1)
    result = evaluate(
        dataset,
        metrics=metrics,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        run_config=run_config,
        raise_exceptions=False
    )
    
    result_df = result.to_pandas()
    
    # Save the partial output to merge later
    out_json = "eval/q14_20_results.json"
    result_df.to_json(out_json, orient="records", indent=4)
    print(f"\\nSaved Q14-20 eval results to {out_json}")

if __name__ == '__main__':
    main()
