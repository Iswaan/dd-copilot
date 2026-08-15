import os
import time
from generation.synthesize import generate_answer, _call_backend

query = "What is the capital of France?"
chunks = [
    {
        "chunk_id": "11111111-1111-1111-1111-111111111111",
        "metadata": {"ticker": "NONE", "filing_type": "WIKI", "date": "2024", "section_heading": "Geography"},
        "text": "The capital of France is Paris. It is a beautiful city."
    }
]

print("Sending minimal test request to OpenRouter...")
start_time = time.time()
try:
    # Directly call the backend to avoid the validation loop for a pure raw connectivity test,
    # or use generate_answer to test the full loop. Let's test the raw backend first, then generate_answer.
    result = generate_answer(query, chunks)
    latency = time.time() - start_time
    print(f"Latency: {latency:.2f}s")
    print(result)
except Exception as e:
    latency = time.time() - start_time
    print(f"Latency: {latency:.2f}s")
    print(f"Error: {e}")
