#!/usr/bin/env python3
"""Index hygiene auditor script for reporting ChromaDB chunk counts, duplicate IDs, and metadata consistency."""

import sys
from pathlib import Path
from collections import Counter

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.rag_engine import vector_collection
from backend.database import get_db_connection

def check_index():
    print("=" * 70)
    print("CHROMADB INDEX HYGIENE & AUDIT REPORT")
    print("=" * 70)

    total_chunks = vector_collection.count()
    print(f"\n[+] Total Chunks Indexed: {total_chunks}")

    all_data = vector_collection.get()
    ids = all_data.get("ids", [])
    metadatas = all_data.get("metadatas", [])

    # Check for Duplicate IDs
    id_counts = Counter(ids)
    duplicates = [id_str for id_str, count in id_counts.items() if count > 1]

    if duplicates:
        print(f"❌ WARNING: Found {len(duplicates)} duplicate chunk IDs in index!")
        for d in duplicates[:5]:
            print(f"   - Duplicate ID: {d}")
    else:
        print("✅ Unique Chunk IDs Check: PASSED (0 duplicates found)")

    # Group Chunks by doc_id
    doc_chunk_counts = Counter()
    missing_meta = 0
    for meta in metadatas:
        if not meta or "doc_id" not in meta:
            missing_meta += 1
        else:
            doc_chunk_counts[meta["doc_id"]] += 1

    print("\n[+] Chunk Distribution per doc_id:")
    for doc_id, count in sorted(doc_chunk_counts.items()):
        print(f"   • {doc_id:<20}: {count} chunks")

    if missing_meta > 0:
        print(f"❌ WARNING: {missing_meta} chunks have missing doc_id metadata!")
    else:
        print("✅ Metadata Consistency Check: PASSED (100% chunks have valid doc_id metadata)")

    # Compare with Source Register in SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doc_id, title FROM source_register")
    registered_docs = dict(cursor.fetchall())
    conn.close()

    print("\n[+] Source Register Audit:")
    for registered_id, title in registered_docs.items():
        indexed_count = doc_chunk_counts.get(registered_id, 0)
        status = "✅ ACTIVE" if indexed_count > 0 else "⚠️ UNINDEXED"
        print(f"   • {registered_id:<20} | {title[:35]:<35} | {indexed_count} chunks | {status}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_index()
