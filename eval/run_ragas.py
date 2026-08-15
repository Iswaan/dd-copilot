import os
import json
import sys
from dotenv import load_dotenv

# Add parent dir to sys.path to resolve retrieval/generation imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch for ragas / langchain-community incompatibility
import langchain_community.chat_models
import langchain_google_vertexai
sys.modules['langchain_community.chat_models.vertexai'] = type('vertexai', (), {'ChatVertexAI': langchain_google_vertexai.ChatVertexAI})

# Load env before imports that might need it
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
    
    print(f"Found {len(eval_items)} eval items to process.")
    
    # Pre-flight check for Groq quota
    estimated_budget = len(eval_items) * 5000
    print(f"Pre-flight check: Testing Groq API quota. Estimated token budget needed: {estimated_budget} tokens...")
    try:
        import groq
        client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
        client.chat.completions.create(
            messages=[{"role": "user", "content": "ping"}],
            model="llama-3.3-70b-versatile",
            max_tokens=5
        )
        print("Pre-flight ping passed. Note: Groq TPD limits are only revealed on a 429 error. The generation loop will catch 429s and abort if TPD is exceeded.")
    except Exception as e:
        print(f"\n[!] Pre-flight check failed! Groq API error: {e}")
        sys.exit(1)
    
    # Initialize pipeline
    print("\nInitializing pipeline...")
    retriever = HybridRetriever()
    
    # Run pipeline
    results_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
        "reference": []  # For ragas v0.2.x compatibility
    }
    
    print("Generating answers for eval set...")
    for item in eval_items:
        q = item["question"]
        print(f"\nProcessing: {q}")
        
        # 1. Retrieve
        # Pass ticker_filter only if it's explicitly provided and non-empty
        ticker = item.get("ground_truth_ticker")
        if ticker:
            candidates = retriever.hybrid_search(q, top_k=20, ticker_filter=ticker)
        else:
            candidates = retriever.hybrid_search(q, top_k=20)
            
        # 2. Rerank
        top_chunks = rerank(q, candidates, top_n=6)
        # 3. Generate
        try:
            gen_result = generate_answer(q, top_chunks)
        except Exception as e:
            if "429" in str(e):
                print(f"\n[!] Generation failed with 429 Rate Limit error: {e}")
                print(f"[!] Aborting early to avoid corrupting the evaluation dataset.")
                import sys
                sys.exit(1)
            else:
                raise e
        
        results_data["question"].append(q)
        results_data["answer"].append(gen_result["answer"])
        results_data["contexts"].append([c["text"] for c in top_chunks])
        results_data["ground_truth"].append(item["ground_truth_answer"])
        results_data["reference"].append(item["ground_truth_answer"])
        
    dataset = Dataset.from_dict(results_data)
    
    # Setup RAGAS Judges using local Ollama
    print("\nSetting up RAGAS judges (Local Ollama llama3:latest)...")
    
    # We use Ollama for RAGAS grading to avoid Groq rate limits and n>1 restrictions
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
    from tqdm import tqdm
    # RAGAS automatically uses tqdm for a visible progress indicator during evaluation
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
    out_json = "eval/results.json"
    result_df.to_json(out_json, orient="records", indent=4)
    
    # Save to MD
    out_md = "eval/results.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# RAGAS Evaluation Results\n\n")
        f.write("> **Note on Judge Model**: The RAGAS LLM judge used here is local `llama3:latest` (via Ollama), while the actual answers were generated by `llama-3.3-70b-versatile` via Groq. This ensures we don't hit strict rate limits during the extensive scoring phase.\n\n")
        f.write("## Aggregate Metrics\n")
        for m in metrics:
            m_name = m.name
            if m_name in result:
                f.write(f"- **{m_name}**: {result[m_name]:.4f}\n")
        
        f.write("\n## Per-Question Results\n\n")
        
        # Display each row
        for _, row in result_df.iterrows():
            f.write(f"### Q: {row['question']}\n")
            f.write(f"**Ground Truth**: {row.get('ground_truth', row.get('reference', ''))}\n\n")
            f.write(f"**Generated Answer**: {row['answer']}\n\n")
            f.write("**Scores**:\n")
            for m in metrics:
                m_name = m.name
                if m_name in row:
                    f.write(f"- {m_name}: {row[m_name]:.4f}\n")
            f.write("\n---\n")
            
    print("\nEvaluation complete. Results saved to eval/results.json and eval/results.md")

if __name__ == "__main__":
    main()
