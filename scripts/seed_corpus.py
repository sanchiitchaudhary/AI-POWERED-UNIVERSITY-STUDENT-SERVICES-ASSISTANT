import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import init_db
from backend.rag_engine import ingest_document_to_vector_store

init_db()

os.makedirs("./data/corpus", exist_ok=True)

# 1. Document 1: General Academic Regulations 2025 (Level 1 Statute)
doc1_path = "./data/corpus/General_Academic_Regulations_2025.txt"
with open(doc1_path, "w") as f:
    f.write("""--- Page 1 ---
Section 1.1: General Degree Requirements
All undergraduate students enrolled in B.Tech Computer Science or related degree programmes must complete a minimum of 120 credits with a Cumulative Grade Point Average (CGPA) of at least 2.0 / 4.0 to qualify for graduation.

Section 2.4: Attendance Mandatory Minimums
As mandated by the University Senate, every student must maintain a minimum of 75% attendance in each registered course to be eligible to sit for end-semester examinations. Subject to clause 3.1, failure to meet 75% attendance results in automatic course detention.

--- Page 2 ---
Section 3.1: Examination Passing Marks
A student is declared passed in a course if they achieve a minimum of 40% marks in the combined internal and end-semester assessments.
""")

# 2. Document 2: Attendance & Condonation Circular 2026 (Level 2 Circular)
doc2_path = "./data/corpus/Attendance_and_Supplementary_Circular_2026.txt"
with open(doc2_path, "w") as f:
    f.write("""--- Page 1 ---
Clause 1.0: Condonation of Attendance Shortage
Effective 2026-09-01, students belonging to batches 2023 onwards with attendance between 65% and 74% may submit a medical certificate or dean's permission letter for condonation of attendance shortage upon payment of the condonation fee.

Clause 2.0: Supplementary Examination Eligibility
Students who secure between 30% and 39% in a regular examination may sit for a supplementary examination. The maximum grade attainable in a supplementary exam is 'C'.
""")

# 3. Document 3: Unofficial Student Guide (Level 5 Content)
doc3_path = "./data/corpus/Student_Council_Unofficial_Tips.txt"
with open(doc3_path, "w") as f:
    f.write("""--- Page 1 ---
Unofficial Tip: Passing Exams without Attendance
Some senior students claim that professors don't check attendance below 60%. Note: This is unofficial advice and not an authorized university rule.
""")

# Ingest all 3 into vector store
res1 = ingest_document_to_vector_store("DOC-REG-2025-01", "University General Academic Regulations 2025", doc1_path, 1, "2025-01-01")
res2 = ingest_document_to_vector_store("DOC-CIRC-2026-04", "Attendance Threshold & Supplementary Rules Circular", doc2_path, 2, "2026-09-01")
res3 = ingest_document_to_vector_store("DOC-UNOFFICIAL-01", "Student Council Exam FAQ & Tips", doc3_path, 5, "2026-01-01")

print(f"Seeded vector corpus: {res1['chunks']} + {res2['chunks']} + {res3['chunks']} chunks indexed.")
