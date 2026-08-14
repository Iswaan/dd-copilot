import os
import json
import logging
import pandas as pd
import re
from unstructured.partition.html import partition_html
from unstructured.partition.pdf import partition_pdf

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_dir = os.path.join(base_dir, "data", "raw", "sec-edgar-filings")
parsed_dir = os.path.join(base_dir, "data", "parsed")
log_file = os.path.join(parsed_dir, "failed.log")

os.makedirs(parsed_dir, exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.ERROR, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_table_html(html_str):
    import io
    import re
    try:
        dfs = pd.read_html(io.StringIO(html_str))
        if dfs:
            df = dfs[0]
            if isinstance(df.columns, pd.MultiIndex):
                headers = [" ".join([str(c) for c in col if not pd.isna(c) and "Unnamed" not in str(c)]) for col in df.columns]
            else:
                headers = [str(c) if not pd.isna(c) and "Unnamed" not in str(c) else "" for c in df.columns]
            
            rows = []
            for _, row in df.iterrows():
                row_list = [str(val) if not pd.isna(val) else "" for val in row.values]
                rows.append(row_list)
                
            # Heuristic to promote first row to headers if default positional indices are used
            if rows and all(str(h) == str(i) for i, h in enumerate(headers)):
                # Find the first row that actually has text
                header_idx = -1
                for idx, r in enumerate(rows):
                    if any(c.strip() for c in r):
                        header_idx = idx
                        break
                
                if header_idx != -1:
                    first_row = rows[header_idx]
                    is_header = True
                    for cell in first_row:
                        cell_clean = cell.strip()
                        if not cell_clean: continue
                        if len(cell_clean) > 200:
                            is_header = False; break
                        # If it looks like a financial number, it's not a header (except years like 2024, 2025)
                        if re.match(r'^[\$\(]?\s*\d{1,3}(,\d{3})*(\.\d+)?\s*[%MKB\)]?$', cell_clean):
                            if not re.match(r'^20\d\d$', cell_clean):
                                is_header = False; break
                    
                    if is_header:
                        headers = first_row
                        rows = rows[header_idx+1:]
            
            # Trim trailing empty strings from headers and rows
            while headers and not str(headers[-1]).strip():
                headers.pop()
            
            for r in rows:
                while r and not str(r[-1]).strip():
                    r.pop()

            return {"caption": "", "headers": headers, "rows": rows}
    except Exception as e:
        return None
    return None

def extract_html_from_full_submission(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    html_start = content.lower().find("<html")
    if html_start != -1:
        html_end = content.lower().rfind("</html>")
        if html_end != -1:
            return content[html_start:html_end+7]
        return content[html_start:]
        
    return content

def process_filing(filepath, ticker, filing_type, date, source_url, is_fallback=False):
    # Normalize date to YYYY-MM-DD
    if len(date) == 8 and date.isdigit():
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    if filepath.endswith('.pdf'):
        elements = partition_pdf(filename=filepath)
    else:
        if is_fallback:
            html_content = extract_html_from_full_submission(filepath)
            elements = partition_html(text=html_content)
        else:
            elements = partition_html(filename=filepath)
    
    sections = []
    tables = []
    
    current_heading = ""
    current_text = []
    
    for element in elements:
        category = element.category
        text_val = str(element).strip()
        
        # SEC heading heuristics
        is_sec_heading = bool(re.match(r'^(?:Part|Item)\s+[0-9A-Za-z]+(?:\.|\s|$)', text_val, re.IGNORECASE))
        is_title = (category == "Title")
        
        if (is_sec_heading or is_title) and len(text_val) > 0 and len(text_val) < 200:
            if current_text:
                sections.append({"heading": current_heading, "text": " ".join(current_text)})
                current_text = []
            current_heading = text_val
        elif category == "Table":
            table_html = getattr(element.metadata, "text_as_html", "")
            table_dict = parse_table_html(table_html) if table_html else None
            
            # fallback caption from preceding text
            fallback_caption = current_text[-1] if current_text else ""
            
            if table_dict:
                if not table_dict["caption"]:
                    table_dict["caption"] = fallback_caption
                tables.append(table_dict)
            else:
                tables.append({"caption": fallback_caption, "headers": [], "rows": [[text_val]]})
        elif category in ["NarrativeText", "Text", "UncategorizedText", "ListItem"]:
            current_text.append(text_val)
            
    if current_text:
        sections.append({"heading": current_heading, "text": " ".join(current_text)})
        
    output = {
        "metadata": {
            "ticker": ticker,
            "filing_type": filing_type,
            "date": date,
            "source_url": source_url
        },
        "sections": sections,
        "tables": tables
    }
    return output

def extract_metadata(acc_dir, accession_num):
    date = accession_num
    cik = ""
    filename = ""
    full_sub_path = os.path.join(acc_dir, "full-submission.txt")
    if os.path.exists(full_sub_path):
        with open(full_sub_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in range(200):
                line = f.readline()
                if not line: break
                if line.startswith("FILED AS OF DATE:"):
                    date = line.split(":")[1].strip()
                if line.strip().startswith("CENTRAL INDEX KEY:"):
                    cik = line.split(":")[1].strip()
                if line.startswith("<FILENAME>") and not filename:
                    filename = line.replace("<FILENAME>", "").strip()

    cik_clean = cik.lstrip('0')
    acc_clean = accession_num.replace("-", "")
    if not filename:
        filename = f"{accession_num}-index.htm"
        
    source_url = f"https://www.sec.gov/Archives/edgar/data/{cik_clean}/{acc_clean}/{filename}"
    return date, source_url

def get_primary_doc_and_fallback(acc_dir):
    files = os.listdir(acc_dir)
    htm_files = [f for f in files if f.endswith('.htm') or f.endswith('.html')]
    if htm_files:
        return os.path.join(acc_dir, htm_files[0]), False
        
    full_sub = os.path.join(acc_dir, "full-submission.txt")
    if os.path.exists(full_sub):
        return full_sub, True
        
    return None, False

def run_parsing(test_mode=False):
    if not os.path.exists(raw_dir):
        print(f"Raw directory not found: {raw_dir}")
        return

    for ticker in os.listdir(raw_dir):
        ticker_dir = os.path.join(raw_dir, ticker)
        if not os.path.isdir(ticker_dir):
            continue
            
        for filing_type in os.listdir(ticker_dir):
            type_dir = os.path.join(ticker_dir, filing_type)
            if not os.path.isdir(type_dir):
                continue
                
            for accession_num in os.listdir(type_dir):
                acc_dir = os.path.join(type_dir, accession_num)
                if not os.path.isdir(acc_dir):
                    continue
                    
                filepath, is_fallback = get_primary_doc_and_fallback(acc_dir)
                if not filepath:
                    continue
                    
                date, source_url = extract_metadata(acc_dir, accession_num)
                
                # Normalize date format for filename
                formatted_date = date
                if len(date) == 8 and date.isdigit():
                    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
                
                print(f"Parsing {ticker} {filing_type} - {formatted_date}")
                try:
                    parsed_data = process_filing(filepath, ticker, filing_type, date, source_url, is_fallback)
                    out_name = f"{ticker}_{filing_type}_{formatted_date}.json"
                    out_path = os.path.join(parsed_dir, out_name)
                    
                    with open(out_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed_data, f, indent=2)
                        
                    if test_mode:
                        return
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")
                    logging.error(f"Failed to parse {ticker} {filing_type} {date}: {e}")

if __name__ == "__main__":
    print("Starting parsing process...")
    run_parsing(test_mode=False)
    print("Parsing complete.")
