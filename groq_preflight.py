import os
import sys
import time
from dotenv import load_dotenv
import groq

load_dotenv()

print("Running improved ~4000 token pre-flight check for Groq quota...")
try:
    client = groq.Groq(api_key=os.environ.get('GROQ_API_KEY'))
    # 4000 words is roughly 5000 tokens, let's use 3000 words.
    dummy_text = "test " * 3500 
    
    start_time = time.time()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text:\n\n{dummy_text}"}
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=50
    )
    print("Pre-flight check PASSED.")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Latency: {time.time() - start_time:.2f}s")
except Exception as e:
    print("\n[!] Pre-flight check FAILED!")
    print(f"Error details: {e}")
    sys.exit(1)
