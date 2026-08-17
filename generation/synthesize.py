import os
import re
import ollama
import groq
import openai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Auto-cascade order: try each in order until one succeeds
MODEL_CASCADE = ["groq", "openrouter", "ollama"]

MODEL_LABELS = {
    "groq": "Groq - GPT-OSS 120B",
    "openrouter": "OpenRouter - GPT-OSS 20B",
    "ollama": "Ollama - Llama 3 8B (Local)",
}

def _call_backend(system_prompt, prompt, backend):
    """Call a specific backend. Returns (text, error) tuple."""
    if backend == "ollama":
        try:
            response = ollama.chat(
                model='llama3:latest',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ]
            )
            return response['message']['content'], None
        except Exception as e:
            return None, f"Ollama Error: {str(e)}"

    elif backend == "groq":
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return None, "Error: GROQ_API_KEY not set."
        client = groq.Groq(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content, None
        except Exception as e:
            err = str(e)
            return None, f"Groq API Error: {err}"

    elif backend == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return None, "Error: OPENROUTER_API_KEY not set."
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            max_retries=0,
        )
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b:free",
                extra_body={"include_reasoning": False},
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content, None
        except Exception as e:
            return None, f"OpenRouter API Error: {str(e)}"

    else:
        return None, f"Error: Unknown backend '{backend}'"


def _call_with_cascade(system_prompt, prompt):
    """Try backends in cascade order. Returns (text, backend_used, error)."""
    last_error = None
    for backend in MODEL_CASCADE:
        print(f"[Cascade] Trying backend: {backend}")
        text, err = _call_backend(system_prompt, prompt, backend)
        if text is not None:
            print(f"[Cascade] Success with backend: {backend}")
            return text, backend, None
        else:
            print(f"[Cascade] Backend '{backend}' failed: {err}")
            last_error = err
    return None, None, last_error


def validate_output(answer_text, chunks):
    lower_ans = answer_text.lower()

    # 1. Reasoning/estimation leakage - model is fabricating instead of citing
    hallucination_phrases = [
        "we need to answer",
        "let's extract",
        "let's analyze",
        "let's assume",
        "we need to determine",
        "i need to ",
        "the user asks",
        "reasoning:",
        "analysis:",
        "chain of thought:",
        "data-driven answer:",
        "it appears that",
        "it is likely that",
        "let me calculate",
        "based on this information, it appears",
        "we can estimate",
        "an educated estimate",
        "approximately $",
        "my estimate",
    ]
    for phrase in hallucination_phrases:
        if phrase in lower_ans:
            return False, f"Hallucination/estimation detected: '{phrase}'"

    # 2. Malformed citations
    for match in re.finditer(r"([a-f0-9\-]{36})", answer_text):
        start, end = match.span()
        if start == 0 or end == len(answer_text) or answer_text[start-1] != '[' or answer_text[end] != ']':
            return False, "Malformed citation detected (must be exactly [chunk_id])"

    # 3. Grounding (unknown citations)
    valid_chunk_ids = {c['chunk_id'] for c in chunks}
    extracted_ids = re.findall(r"\[([a-f0-9\-]{36})\]", answer_text)
    for cid in extracted_ids:
        if cid not in valid_chunk_ids:
            return False, f"Unknown citation detected: [{cid}]"

    # 4. Structure check (only if answer has citations — pure refusals are fine)
    has_summary = "Summary:" in answer_text
    has_key_findings = "Key Findings:" in answer_text

    if len(extracted_ids) > 0:
        if not (has_summary and has_key_findings):
            return False, "Supported answer missing Summary or Key Findings"

    return True, ""


def generate_answer(query: str, chunks: list) -> dict:
    chunks_text = ""
    for c in chunks:
        chunks_text += f"\n<chunk id=\"{c['chunk_id']}\">\nSource: {c['metadata']['ticker']} {c['metadata']['filing_type']} - {c['metadata']['section_heading']}\n{c['text']}\n</chunk>\n"

    system_prompt = """You are a strict financial due diligence AI. You answer ONLY from the provided SEC filing chunks. Fabricating, estimating, or reasoning beyond the text is FORBIDDEN.

RULES (follow exactly):
1. REFUSAL: If the chunks contain no relevant information, say in 1-2 sentences that the information is not available in the provided filings. Do NOT estimate, guess, or calculate.
2. PARTIAL ANSWER: If chunks have partial relevant info, use only what is explicitly stated. Cite every fact. Caveat gaps in Risks/Caveats.
3. CITATIONS: Every factual claim MUST end with [chunk_id] in exactly this format. No labels, no prefixes inside brackets.
4. NO FABRICATION: Do NOT use phrases like "let's assume", "approximately", "we can estimate", "it appears", "likely to be", or any arithmetic invented by you. Only cite what is literally in the text.
5. FORMAT (when citations exist):
   Summary: (2-3 sentences, factual only)
   Key Findings:
   - finding [chunk_id]
   Risks/Caveats: (gaps or limitations)"""

    original_prompt = f"User Query: {query}\n\nProvided Chunks:\n{chunks_text}"
    prompt = original_prompt

    max_retries = 2
    attempts = 0
    answer_text = ""
    backend_used = None

    while attempts <= max_retries:
        if attempts > 0:
            retry_instruction = (
                "IMPORTANT: Your previous response was REJECTED. You violated the rules by estimating, reasoning, or fabricating data. "
                "Regenerate the answer using ONLY facts explicitly stated in the chunk text above. "
                "If the exact information is not in the chunks, respond with a 1-2 sentence refusal. "
                "Do NOT calculate, estimate, or assume anything. Every claim must have a [chunk_id] citation."
            )
            prompt = f"{original_prompt}\n\n{retry_instruction}"

        text, used_backend, err = _call_with_cascade(system_prompt, prompt)

        if text is None:
            answer_text = f"Error: All LLM backends failed. Last error: {err}"
            break

        backend_used = used_backend
        answer_text = text

        is_valid, error_msg = validate_output(answer_text, chunks)

        if is_valid:
            print(f"Generation succeeded on attempt {attempts} via {backend_used}")
            break
        else:
            print(f"Validation failed on attempt {attempts}: {error_msg}")
            if attempts == max_retries:
                # Force a clean refusal rather than surfacing a hallucinated answer
                answer_text = "The information requested could not be found in the indexed SEC filing chunks. Please try rephrasing your question or check that the relevant filing has been indexed."
                print(f"Max retries exhausted, returning safe refusal.")
                break

        attempts += 1

    # Extract citations strictly
    valid_chunk_ids = {c['chunk_id'] for c in chunks}
    extracted_ids = list(set(re.findall(r"\[([a-f0-9\-]{36})\]", answer_text)))

    citations = []
    valid_cited_ids = []
    invalid_cited_ids = []

    for cid in extracted_ids:
        if cid in valid_chunk_ids:
            valid_cited_ids.append(cid)
            for c in chunks:
                if c['chunk_id'] == cid:
                    citations.append({
                        "chunk_id": cid,
                        "ticker": c["metadata"]["ticker"],
                        "filing_type": c["metadata"]["filing_type"],
                        "source_url": c["metadata"].get("source_url", ""),
                        "section_heading": c["metadata"]["section_heading"]
                    })
                    break
        else:
            invalid_cited_ids.append(cid)

    return {
        "answer": answer_text,
        "citations": citations,
        "raw_chunks_used": valid_cited_ids,
        "invalid_citations": invalid_cited_ids,
        "model_used": MODEL_LABELS.get(backend_used, backend_used or "unknown"),
    }

