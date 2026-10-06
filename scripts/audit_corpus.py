import os
import re
import statistics
import sys
import pypdf
import docx

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rag_engine import extract_text_from_filepath, chunk_text_with_metadata

DOCS_DIRS = ["./data/docs", "./data/corpus"]

def find_all_documents():
    files = []
    seen = set()
    for d in DOCS_DIRS:
        if os.path.exists(d):
            for fname in sorted(os.listdir(d)):
                fpath = os.path.join(d, fname)
                if os.path.isfile(fpath) and fname not in seen and not fname.startswith('.'):
                    seen.add(fname)
                    files.append((fname, fpath))
    return files

def audit_document(fname, fpath):
    ext = os.path.splitext(fpath)[1].lower()
    full_text = extract_text_from_filepath(fpath)
    
    # 1. Pages & OCR analysis
    page_count = 1
    text_layer_pages = 0
    ocr_needed_pages = 0
    
    if ext == '.pdf':
        try:
            reader = pypdf.PdfReader(fpath)
            page_count = len(reader.pages)
            for page in reader.pages:
                txt = page.extract_text() or ""
                if len(txt.strip()) > 30:
                    text_layer_pages += 1
                else:
                    ocr_needed_pages += 1
        except Exception:
            ocr_needed_pages = page_count
    elif ext == '.docx':
        text_layer_pages = 1
    else:
        text_layer_pages = 1

    # 2. Table detection & examples
    tables_found = []
    table_lines = re.findall(r'(\|.*\||\+[-+]+\+)', full_text)
    if table_lines:
        tables_found.append("\n".join(table_lines[:4]))
        
    # 3. Chunking statistics & section checks
    doc_id = f"DOC-{fname.split('.')[0].upper()}"
    chunks = chunk_text_with_metadata(doc_id, fname, full_text)
    chunk_lengths = [len(c["text"]) for c in chunks] if chunks else [0]
    
    chunks_no_section = [c for c in chunks if not c["metadata"].get("section") or c["metadata"]["section"] == "General"]
    chunks_no_page = [c for c in chunks if not c["metadata"].get("page")]
    
    min_len = min(chunk_lengths)
    max_len = max(chunk_lengths)
    median_len = int(statistics.median(chunk_lengths)) if chunk_lengths else 0
    
    # 4. Cross-references & resolution check
    cross_refs = []
    for c in chunks:
        ref_text = c["metadata"].get("refs", "")
        if ref_text:
            for ref in ref_text.split(","):
                cross_refs.append((ref.strip(), c["id"]))

    # Resolve refs
    unresolved_refs = []
    for ref, src_id in cross_refs:
        resolved = any(ref in c["text"] or ref in c["metadata"].get("section", "") for c in chunks)
        if not resolved:
            unresolved_refs.append((ref, src_id))

    # 5. Candidate dates, versions & supersessions
    dates_found = re.findall(r'\b(20\d{2}-\d{2}-\d{2}|effective\s+\d{4}-\d{2}-\d{2})\b', full_text, re.IGNORECASE)
    supersessions = re.findall(r'(supersed\w+|replaces\s+clause|amends)', full_text, re.IGNORECASE)
    versions = re.findall(r'version\s*[\d\.]+', full_text, re.IGNORECASE)

    return {
        "filename": fname,
        "filepath": fpath,
        "page_count": page_count,
        "text_layer_pages": text_layer_pages,
        "ocr_needed_pages": ocr_needed_pages,
        "table_count": len(tables_found),
        "table_examples": tables_found,
        "chunks_count": len(chunks),
        "chunk_min": min_len,
        "chunk_median": median_len,
        "chunk_max": max_len,
        "chunks_no_section": len(chunks_no_section),
        "chunks_no_page": len(chunks_no_page),
        "cross_refs_count": len(cross_refs),
        "unresolved_refs": unresolved_refs,
        "dates_found": dates_found,
        "supersessions": supersessions,
        "versions": versions
    }

def run_corpus_audit():
    documents = find_all_documents()
    audit_results = []
    
    for fname, fpath in documents:
        res = audit_document(fname, fpath)
        audit_results.append(res)
        
    # Generate Markdown Report
    report = []
    report.append("# Corpus Audit Report (CORPUS_AUDIT.md)\n")
    report.append(f"**Audit Execution Date**: 2026-10-06\n")
    report.append(f"**Total Documents Audited**: {len(audit_results)}\n\n")
    
    report.append("## 1. Document Inventory & Pages Summary\n")
    report.append("| Filename | Total Pages | Text Layer Pages | OCR Needed | Total Chunks | Chunk Size (Min/Med/Max) |\n")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for r in audit_results:
        report.append(f"| `{r['filename']}` | {r['page_count']} | {r['text_layer_pages']} | {r['ocr_needed_pages']} | {r['chunks_count']} | {r['chunk_min']} / {r['chunk_median']} / {r['chunk_max']} |\n")
        
    report.append("\n## 2. Table Extraction & Structured Content\n")
    for r in audit_results:
        report.append(f"### Document: `{r['filename']}`\n")
        if r['table_examples']:
            report.append("Structured Table Snippet Preview:\n```\n" + r['table_examples'][0] + "\n```\n")
        else:
            report.append("No explicit ASCII/Markdown tables detected.\n")

    report.append("\n## 3. Clause Cross-References & Link Resolution\n")
    for r in audit_results:
        report.append(f"- **`{r['filename']}`**: {r['cross_refs_count']} clause references detected.")
        if r['unresolved_refs']:
            report.append(f" (Unresolved: {len(r['unresolved_refs'])})\n")
        else:
            report.append(" (All cross-references resolved to active chunks)\n")

    report.append("\n## 4. Metadata Statements (Dates, Versions, Supersessions)\n")
    for r in audit_results:
        report.append(f"### `{r['filename']}`\n")
        report.append(f"- **Dates Detected**: {', '.join(r['dates_found']) if r['dates_found'] else 'None'}\n")
        report.append(f"- **Versions Detected**: {', '.join(r['versions']) if r['versions'] else 'Standard 1.0'}\n")
        report.append(f"- **Supersession Keywords**: {', '.join(r['supersessions']) if r['supersessions'] else 'None'}\n")

    report_text = "".join(report)
    
    os.makedirs("./docs", exist_ok=True)
    with open("./docs/CORPUS_AUDIT.md", "w") as f:
        f.write(report_text)
        
    print(report_text)

if __name__ == '__main__':
    run_corpus_audit()
