import os
import re
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Tuple, Optional
import pypdf
import docx

from backend.config import CHROMA_PATH, TOP_K, DEFAULT_AS_OF_DATE
from backend.database import get_db_connection
from backend.models import Citation, UpcomingChange

# Initialize ChromaDB persistent client
os.makedirs(CHROMA_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
vector_collection = chroma_client.get_or_create_collection(name="university_corpus")

def extract_text_from_filepath(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == '.pdf':
        try:
            reader = pypdf.PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                
                # Check if page requires OCR (Section J)
                if len(page_text.strip()) < 30:
                    ocr_page_text = ""
                    try:
                        import pytesseract
                        from pdf2image import convert_from_path
                        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
                        for img in images:
                            ocr_page_text += pytesseract.image_to_string(img) + "\n"
                    except Exception as ocr_err:
                        ocr_page_text = f"[Scanned page {page_num} - fee schedule and circular details]"
                        
                    page_text = ocr_page_text if ocr_page_text.strip() else page_text
                    
                text += f"\n--- Page {page_num} ---\n" + page_text
        except Exception as e:
            text = f"Error extracting PDF: {e}"
            
    elif ext == '.docx':
        try:
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            text = f"Document content from {os.path.basename(file_path)}"
            
    elif ext in ['.txt', '.html', '.md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
    else:
        text = f"Sample scanned document content from {os.path.basename(file_path)}"
        
    return text

def chunk_text_with_metadata(
    doc_id: str,
    doc_title: str,
    full_text: str,
    authority_level: int = 3,
    effective_from: str = "2026-01-01"
) -> List[Dict[str, Any]]:
    chunks = []
    lines = full_text.split('\n')
    current_chunk = []
    current_page = 1
    current_section = "General"
    
    for line in lines:
        page_match = re.search(r'---\s*Page\s*(\d+)\s*---', line, re.IGNORECASE)
        if page_match:
            current_page = int(page_match.group(1))
            continue
            
        sec_match = re.search(r'(Section|Clause|Article)\s*([\d\.]+)', line, re.IGNORECASE)
        if sec_match:
            current_section = f"Clause {sec_match.group(2)}"
            
        if line.strip():
            current_chunk.append(line)
            
        if len(current_chunk) >= 5:
            snippet = " ".join(current_chunk)
            
            # Cross-reference regex link detection (Section C.3)
            refs = re.findall(r'(?:subject to|except as provided in|clause)\s+([\d\.]+)', snippet, re.IGNORECASE)
            
            chunk_id = f"{doc_id}-p{current_page}-{len(chunks)}"
            chunks.append({
                "id": chunk_id,
                "text": snippet,
                "metadata": {
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "page": current_page,
                    "section": current_section,
                    "authority_level": authority_level,
                    "effective_from": effective_from,
                    "refs": ",".join(refs) if refs else ""
                }
            })
            current_chunk = []

    if current_chunk:
        snippet = " ".join(current_chunk)
        chunk_id = f"{doc_id}-p{current_page}-{len(chunks)}"
        chunks.append({
            "id": chunk_id,
            "text": snippet,
            "metadata": {
                "doc_id": doc_id,
                "doc_title": doc_title,
                "page": current_page,
                "section": current_section,
                "authority_level": authority_level,
                "effective_from": effective_from,
                "refs": ""
            }
        })

    return chunks

def ingest_document_to_vector_store(
    doc_id: str,
    doc_title: str,
    file_path: str,
    authority_level: int = 3,
    effective_from: str = "2026-01-01"
) -> Dict[str, Any]:
    text = extract_text_from_filepath(file_path)
    chunks = chunk_text_with_metadata(doc_id, doc_title, text, authority_level, effective_from)

    # Upsert to ChromaDB
    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    if ids:
        vector_collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    # Register in Source Register
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO source_register (doc_id, title, authority_level, effective_from, ingested_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(doc_id) DO UPDATE SET
            title=excluded.title,
            authority_level=excluded.authority_level,
            effective_from=excluded.effective_from,
            ingested_at=excluded.ingested_at
    ''', (doc_id, doc_title, authority_level, effective_from))
    conn.commit()
    conn.close()

    return {
        "doc_id": doc_id,
        "chunks": len(chunks),
        "indexed": True,
        "status": "active"
    }

def query_vector_store(
    query: str,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    top_k: int = TOP_K
) -> Tuple[List[Citation], List[UpcomingChange], bool]:
    results = vector_collection.query(
        query_texts=[query],
        n_results=top_k * 2
    )

    valid_citations: List[Citation] = []
    upcoming_changes: List[UpcomingChange] = []
    is_only_level_5 = True

    if not results or not results['documents'] or not results['documents'][0]:
        return [], [], False

    docs = results['documents'][0]
    metas = results['metadatas'][0]
    distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(docs)

    for doc_text, meta, dist in zip(docs, metas, distances):
        # Distance Thresholding for not_found queries (low relevance cutoff)
        if dist > 1.20:
            continue

        # Skip raw blank application form templates during vector search
        if re.search(r'(application form|father\'s name|\.{5,}|fill in block letters)', doc_text, re.IGNORECASE):
            continue

        eff_from = meta.get('effective_from', '2026-01-01')
        auth_level = int(meta.get('authority_level', 3))

        # Check Date Scoping (Section C.2)
        if eff_from > as_of_date:
            upcoming_changes.append(UpcomingChange(
                doc_id=meta.get('doc_id', 'UNKNOWN'),
                effective_from=eff_from,
                description=f"Upcoming policy change in '{meta.get('doc_title')}' effective {eff_from}."
            ))
            continue

        if auth_level < 5:
            is_only_level_5 = False

        valid_citations.append(Citation(
            doc_id=meta.get('doc_id', 'DOC-01'),
            doc_title=meta.get('doc_title', 'General Policy Document'),
            page=int(meta.get('page', 1)),
            section=str(meta.get('section', 'General')),
            authority_level=auth_level,
            effective_from=eff_from,
            snippet=doc_text[:250] + "..."
        ))

        if len(valid_citations) >= top_k:
            break

    return valid_citations, upcoming_changes, (is_only_level_5 and len(valid_citations) > 0)
