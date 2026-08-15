def score_confidence(chunks_used: list, rerank_scores: list) -> str:
    """
    Score the confidence of the generated answer based on the chunks used.
    Note: This is a v1 heuristic.
    """
    if not chunks_used or not rerank_scores:
        return "low"
        
    avg_score = sum(rerank_scores) / len(rerank_scores)
    num_distinct = len(set([c["chunk_id"] for c in chunks_used]))
    
    # v1 heuristic logic
    if avg_score > 0.7 and num_distinct >= 2:
        return "high"
    elif avg_score > 0.4:
        return "medium"
    else:
        return "low"
