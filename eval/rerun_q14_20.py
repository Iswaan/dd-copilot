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
    
    # Target only Q14-20
    eval_items = eval_items[13:20]
    print(f"Found {len(eval_items)} eval items to process (Q14-20).")
    
    partial_results_file = "eval/partial_results.json"
    saved_results = []
    saved_questions = set()
    
    if os.path.exists(partial_results_file):
        try:
            with open(partial_results_file, "r", encoding="utf-8") as f:
                saved_results = json.load(f)
            saved_questions = {res["question"] for res in saved_results}
            print(f"Loaded {len(saved_results)} previously saved validated results from {partial_results_file}.")
        except Exception as e:
            print(f"Error loading {partial_results_file}: {e}")
            sys.exit(1)
            
    # Initialize pipeline
    print("\nInitializing pipeline...")
    retriever = HybridRetriever()
    
    succeeded_indices = []
    
    print("\nGenerating answers for Q14-20...")
    for idx, item in enumerate(eval_items):
        q_idx = 14 + idx
        q = item["question"]
        
        if q in saved_questions:
            print(f"\nSkipping Q{q_idx}: Already validated and saved.")
            succeeded_indices.append(q_idx)
            continue
            
        print(f"\nProcessing Q{q_idx}: {q}")
        
        ticker = item.get("ground_truth_ticker")
        if ticker and ticker != "multi":
            candidates = retriever.hybrid_search(q, top_k=20, ticker_filter=ticker)
        else:
            candidates = retriever.hybrid_search(q, top_k=20)
            
        top_chunks = rerank(q, candidates, top_n=6)
        
        try:
            gen_result = generate_answer(q, top_chunks)
            ans = gen_result["answer"]
            
            # Content-validation checks before proceeding
            if "API Error" in ans or "rate-limit" in ans:
                raise Exception(f"API Error string leaked into output: {ans[:100]}")
                
            if "Summary:" not in ans or "Key Findings:" not in ans:
                # Allow strict refusal cases
                if "I'm sorry" not in ans and "I am sorry" not in ans and "not contain" not in ans:
                    raise Exception("Output missing structural headers (Summary/Key Findings)!")
                    
        except Exception as e:
            print(f"\n[!] Generation failed at Q{q_idx} with error: {e}")
            print(f"Succeeded Qs this run: {succeeded_indices}")
            print("Aborting immediately to prevent merging partial data. Saved questions remain safe on disk.")
            sys.exit(1)
            
        # Immediately save this question's result
        saved_results.append({
            "question": q,
            "answer": gen_result["answer"],
            "contexts": [c["text"] for c in top_chunks],
            "ground_truth": item["ground_truth_answer"],
            "reference": item["ground_truth_answer"]
        })
        
        with open(partial_results_file, "w", encoding="utf-8") as f:
            json.dump(saved_results, f, indent=4)
            
        print(f"Q{q_idx} validated and saved successfully.")
        succeeded_indices.append(q_idx)
        
    print(f"\nAll 7 generation steps completed successfully! (Q14-20)")
    
    results_data = {
        "question": [res["question"] for res in saved_results],
        "answer": [res["answer"] for res in saved_results],
        "contexts": [res["contexts"] for res in saved_results],
        "ground_truth": [res["ground_truth"] for res in saved_results],
        "reference": [res["reference"] for res in saved_results]
    }
        
    dataset = Dataset.from_dict(results_data)
    
    # Setup RAGAS Judges using local Ollama
    print("\nSetting up RAGAS judges (Local Ollama llama3:latest)...")
    llm = ChatOllama(model="llama3:latest", base_url="http://localhost:11434", temperature=0.0)
    ragas_llm = LangchainLLMWrapper(llm)
    
    embeddings_wrapper = SentenceTransformerWrapper(retriever.embed_model)
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings_wrapper)
    
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
    
    print("Running RAGAS evaluation (this may take several minutes with local inference)...")
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
    
    # Save to JSON
    out_json = "eval/q14_20_results.json"
    result_df.to_json(out_json, orient="records", indent=4)
    
    print(f"\nEvaluation complete. Final Q14-20 results saved to {out_json}.")
    print(f"You can now run merge_results.py to merge these with Q1-13.")

if __name__ == "__main__":
    main()
