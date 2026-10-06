import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import init_db
from backend.rag_engine import ingest_document_to_vector_store

init_db()

docs_to_ingest = [
    ("DOC-ACAD-2024", "Academic Regulations 2024 (BTech/MTech)", "./data/docs/ACAD-REG-2024_Academic_Regulations_BTech_MTech (1).pdf", 1, "2024-07-01"),
    ("DOC-PLACEMENT", "University Placement & Internship Policy", "./data/docs/Placement+Policy.pdf", 2, "2024-06-01"),
    ("DOC-CVSPK-SCH", "CVSPK Scholarship Guidelines 2024-25", "./data/docs/CVSPK scholarships guidelines.pdf", 2, "2024-08-15"),
    ("DOC-ETHICS", "Digital Ethics & AI Policy Guidelines", "./data/docs/DIGITAL ETHICS GUIDELINES.pdf", 3, "2024-01-01"),
    ("DOC-FEE-SCHED", "Fee Structure III V VII Semesters", "./data/docs/fee III V VII.pdf", 3, "2024-07-15"),
    ("DOC-SUMMER", "Summer Semester Guidelines", "./data/docs/summer semester.pdf", 3, "2024-05-01"),
    ("DOC-REG-2025-01", "University General Academic Regulations 2025", "./data/docs/General_Academic_Regulations_2025.txt", 1, "2025-01-01"),
    ("DOC-CIRC-2026-04", "Attendance Threshold & Supplementary Rules Circular", "./data/docs/Attendance_and_Supplementary_Circular_2026.txt", 2, "2026-09-01"),
    ("DOC-UNOFFICIAL-01", "Student Council Exam FAQ & Tips", "./data/docs/Student_Council_Unofficial_Tips.txt", 5, "2026-01-01")
]

total_indexed_chunks = 0

for doc_id, doc_title, fpath, auth_level, eff_from in docs_to_ingest:
    if os.path.exists(fpath):
        res = ingest_document_to_vector_store(doc_id, doc_title, fpath, auth_level, eff_from)
        print(f"Indexed {doc_title} ({doc_id}): {res['chunks']} chunks.")
        total_indexed_chunks += res['chunks']
    else:
        print(f"Warning: File {fpath} not found.")

print(f"\nIngestion Complete! Total {total_indexed_chunks} chunks stored in ChromaDB.")
