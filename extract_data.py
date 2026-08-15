import json
import os
import glob

parsed_dir = 'data/parsed'

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_sections(data, keywords):
    results = []
    for sec in data.get('sections', []):
        text = sec.get('text', '').lower()
        if all(kw.lower() in text for kw in keywords):
            results.append((sec.get('heading', ''), sec.get('text', '')))
    return results

def search_tables(data, keywords):
    results = []
    for tab in data.get('tables', []):
        cap = tab.get('caption', '').lower()
        content = str(tab.get('headers', [])) + str(tab.get('rows', []))
        content = content.lower()
        if all(kw.lower() in cap or kw.lower() in content for kw in keywords):
            results.append((tab.get('caption', ''), tab.get('rows', [])[:3])) # print first few rows
    return results

print("=== Q1: AAPL Supply Chain Risks ===")
aapl_10k = load_json(os.path.join(parsed_dir, 'AAPL_10-K_2025-10-31.json'))
print(search_sections(aapl_10k, ['supply chain', 'risk'])[0][1][:300] if search_sections(aapl_10k, ['supply chain', 'risk']) else "Not found")

print("\n=== Q2: AAPL Stock Class and Exchange ===")
print(search_sections(aapl_10k, ['exchange', 'registered', 'common stock'])[0][1][:300] if search_sections(aapl_10k, ['exchange', 'registered', 'common stock']) else "Not found")
print(search_tables(aapl_10k, ['common stock', 'trading symbol'])[:1] if search_tables(aapl_10k, ['common stock', 'trading symbol']) else "Not found in tables")

print("\n=== Q3: AAPL Cash and Marketable Securities (10-Q) ===")
aapl_10q = load_json(os.path.join(parsed_dir, 'AAPL_10-Q_2026-07-31.json'))
print(search_sections(aapl_10q, ['cash', 'marketable securities'])[0][1][:300] if search_sections(aapl_10q, ['cash', 'marketable securities']) else "Not found")

print("\n=== Q4: MSFT Azure Revenue Growth ===")
msft_10q = load_json(os.path.join(parsed_dir, 'MSFT_10-Q_2026-04-29.json'))
print(search_sections(msft_10q, ['azure', 'revenue', 'growth'])[0][1][:300] if search_sections(msft_10q, ['azure', 'revenue', 'growth']) else "Not found")

print("\n=== Q5: MSFT Antitrust Risks ===")
msft_10k = load_json(os.path.join(parsed_dir, 'MSFT_10-K_2026-07-29.json'))
print(search_sections(msft_10k, ['antitrust'])[0][1][:300] if search_sections(msft_10k, ['antitrust']) else "Not found")

print("\n=== Q6: MSFT Dividend or Share Repurchase ===")
print(search_tables(msft_10k, ['dividend', 'repurchase'])[:1] if search_tables(msft_10k, ['dividend', 'repurchase']) else "Not found")

print("\n=== Q7: JPM Credit Risk Exposures ===")
jpm_10k = load_json(os.path.join(parsed_dir, 'JPM_10-K_2026-02-13.json'))
print(search_sections(jpm_10k, ['credit risk exposure'])[0][1][:300] if search_sections(jpm_10k, ['credit risk exposure']) else "Not found")

print("\n=== Q8: JPM CET1 Ratio ===")
print(search_tables(jpm_10k, ['cet1'])[:1] if search_tables(jpm_10k, ['cet1']) else "Not found")

print("\n=== Q9: JPM Litigation ===")
print(search_sections(jpm_10k, ['litigation', 'legal proceedings'])[0][1][:300] if search_sections(jpm_10k, ['litigation', 'legal proceedings']) else "Not found")

print("\n=== Q10: PFE R&D Spending ===")
pfe_10q = load_json(os.path.join(parsed_dir, 'PFE_10-Q_2026-08-04.json'))
print(search_sections(pfe_10q, ['research and development', 'expense'])[0][1][:300] if search_sections(pfe_10q, ['research and development', 'expense']) else "Not found")

print("\n=== Q11: PFE Patent Expiration ===")
pfe_10k = load_json(os.path.join(parsed_dir, 'PFE_10-K_2026-02-26.json'))
print(search_sections(pfe_10k, ['patent expiration', 'risk'])[0][1][:300] if search_sections(pfe_10k, ['patent expiration', 'risk']) else "Not found")

print("\n=== Q12: TSLA Gigafactory ===")
tsla_10k = load_json(os.path.join(parsed_dir, 'TSLA_10-K_2026-01-29.json'))
print(search_sections(tsla_10k, ['gigafactory', 'expand'])[0][1][:300] if search_sections(tsla_10k, ['gigafactory', 'expand']) else "Not found")

print("\n=== Q13: Cross-ticker Revenue ===")
print("MSFT:", search_sections(msft_10k, ['total revenue'])[0][1][:200] if search_sections(msft_10k, ['total revenue']) else "Not found")
print("AAPL:", search_sections(aapl_10k, ['total net sales'])[0][1][:200] if search_sections(aapl_10k, ['total net sales']) else "Not found")
print("TSLA:", search_sections(tsla_10k, ['total revenues'])[0][1][:200] if search_sections(tsla_10k, ['total revenues']) else "Not found")

print("\n=== Q14: Cybersecurity Incidents ===")
found = False
for f in glob.glob(os.path.join(parsed_dir, '*.json')):
    data = load_json(f)
    if search_sections(data, ['cybersecurity incident']):
        print(f"Found in {f}: {search_sections(data, ['cybersecurity incident'])[0][1][:200]}")
        found = True
if not found:
    print("None of the 5 companies disclose cybersecurity incidents in their filings.")
