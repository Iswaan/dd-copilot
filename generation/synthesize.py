import os
import re
import anthropic
import ollama
import groq
import openai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

GENERATION_BACKEND = "groq"

def _call_backend(system_prompt, prompt, model_override=None):
    backend_to_use = model_override if model_override else GENERATION_BACKEND
    if backend_to_use == "ollama":
        try:
            response = ollama.chat(
                model='llama3:latest',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Ollama Error: {str(e)}"
            
    elif backend_to_use == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Error: ANTHROPIC_API_KEY not set."
        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"API Error: {str(e)}"
            
    elif backend_to_use == "groq":
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return "Error: GROQ_API_KEY not set."
        client = groq.Groq(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq API Error: {str(e)}"
            
    elif backend_to_use == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return "Error: OPENROUTER_API_KEY not set."
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            max_retries=0, # Disable automatic hangs
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
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenRouter API Error: {str(e)}"
    
    else:
        return f"Error: Unknown GENERATION_BACKEND '{backend_to_use}'"

def validate_output(answer_text, chunks):
    # 1. Reasoning leakage
    leakage_phrases = [
        "we need to answer",
        "let's extract",
        "let's analyze",
        "we need to determine",
        "i need to ",
        "the user asks",
        "reasoning:",
        "analysis:",
        "chain of thought:"
    ]
    lower_ans = answer_text.lower()
    for phrase in leakage_phrases:
        if phrase in lower_ans:
            return False, f"Reasoning leakage detected: '{phrase}'"
            
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
            
    # 4. Structure
    has_summary = "Summary:" in answer_text
    has_key_findings = "Key Findings:" in answer_text
    
    if len(extracted_ids) > 0:
        if not (has_summary and has_key_findings):
            return False, "Supported answer missing Summary or Key Findings"
            
    return True, ""

def generate_answer(query: str, chunks: list, model_override: str = None) -> dict:
    chunks_text = ""
    for c in chunks:
        chunks_text += f"\n<chunk id=\"{c['chunk_id']}\">\nSource: {c['metadata']['ticker']} {c['metadata']['filing_type']} - {c['metadata']['section_heading']}\n{c['text']}\n</chunk>\n"

    system_prompt = """You are a meticulous financial due diligence AI. You answer user queries based strictly on the provided SEC filing chunks.
Follow these rules:
1. TRUE REFUSAL CASE (e.g. asking for a forward-looking stock price target, which SEC filings never disclose): If the retrieved chunks contain no information at all relevant to the question, refuse in 1-2 sentences. Do not summarize unrelated information from the chunks first.
2. PARTIAL/NARRATIVE CASE (e.g. asking for debt maturities when no dedicated debt maturity table exists): If the retrieved chunks don't contain a clean, structured, complete answer, but DO contain genuinely relevant partial information (e.g. narrative disclosures about credit risk, liquidity, or debt-adjacent context), synthesize an answer from what's actually there. Cite it normally, and explicitly caveat in the Risks/Caveats section that no dedicated/structured disclosure was found and this is based on partial narrative information. Do NOT refuse outright.
3. Every factual claim must be followed by an inline citation pointing to the specific chunk it came from, using the exact format: [chunk_id]. Citations must appear in EXACTLY this format: [chunk_id] - for example [da8c968c-ea13-421d-9d7b-fc6c2b288455]. Do not add labels, prefixes, or extra text inside the brackets.
4. Structure the answer exactly as follows (omitting Risks/Caveats if not applicable):
Summary: (2-3 sentences)
Key Findings: (bulleted, each with a citation)
Risks/Caveats: (data-gap caveats or limitations)"""

    original_prompt = f"User Query: {query}\n\nProvided Chunks:\n{chunks_text}"
    prompt = original_prompt
    
    max_retries = 2
    attempts = 0
    answer_text = ""
    
    while attempts <= max_retries:
        if attempts > 0:
            retry_instruction = "Your previous response violated the required output format. Regenerate ONLY the final answer. Do not include analysis, planning, or meta-commentary. Use only the supplied context. Every factual claim must use an exact [chunk_id] citation corresponding to a retrieved chunk. Preserve the required Summary, Key Findings, and Risks/Caveats structure where applicable."
            prompt = f"{original_prompt}\n\n{retry_instruction}"

        answer_text = _call_backend(system_prompt, prompt, model_override=model_override)
        
        if "Error:" in answer_text or "API Error" in answer_text:
            break
            
        is_valid, error_msg = validate_output(answer_text, chunks)
        
        if is_valid:
            print(f"Generation succeeded on attempt {attempts}")
            break
        else:
            print(f"Validation failed on attempt {attempts}: {error_msg}")
            if attempts == max_retries:
                answer_text = f"Validation Error: Maximum retries exhausted. Last error: {error_msg}\n\nLast output:\n{answer_text}"
                break
        
        attempts += 1

    # Extract citations strictly
    import re
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
        "invalid_citations": invalid_cited_ids
    }

