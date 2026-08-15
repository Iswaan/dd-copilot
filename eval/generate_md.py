import json
import os

with open('eval/results.json', 'r') as f:
    data = json.load(f)

with open('eval/results.md', 'w') as f:
    f.write('# RAGAS Evaluation Results\n\n')
    f.write('> **Note on Execution**: RAGAS evaluation was run, but hit severe rate limits using Groq free tier. Scores are `NaN` because RAGAS dropped those computations due to API errors (Rate Limit and BadRequest for `n>1`). The generated answers below are 100% real outputs from the actual pipeline run. Any items that failed during generation due to the API limit show the raw API error.\n\n')
    
    for row in data:
        f.write(f"### Q: {row.get('user_input', '')}\n")
        f.write(f"**Ground Truth**: {row.get('reference', '')}\n\n")
        f.write(f"**Generated Answer**: {row.get('response', '')}\n\n")
        f.write("**Scores (INCOMPLETE due to rate limit)**:\n")
        f.write(f"- faithfulness: {row.get('faithfulness', 'NaN')}\n")
        f.write(f"- answer_relevancy: {row.get('answer_relevancy', 'NaN')}\n")
        f.write(f"- context_precision: {row.get('context_precision', 'NaN')}\n")
        f.write(f"- context_recall: {row.get('context_recall', 'NaN')}\n")
        f.write('\n---\n')

print("Updated results.md")
