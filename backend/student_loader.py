import csv
import io
from typing import List, Dict, Any, Tuple
from backend.database import get_db_connection

# Expected header sets for target table auto-detection
HEADER_SCHEMAS = {
    'students': {'student_id', 'name'},
    'courses': {'course_code', 'title'},
    'attendance': {'student_id', 'course_code', 'attendance_pct'},
    'results': {'student_id', 'course_code', 'marks'}
}

def detect_table_by_headers(headers: List[str]) -> str:
    header_set = {h.strip().lower() for h in headers}
    
    for table_name, req_headers in HEADER_SCHEMAS.items():
        if req_headers.issubset(header_set):
            return table_name
            
    raise ValueError(f"Could not identify database target table from headers: {headers}")

def process_csv_content(csv_text: str) -> Dict[str, Any]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        return {"status": "error", "message": "Empty or invalid CSV content."}

    # Normalize headers
    normalized_fieldnames = [f.strip().lower() for f in reader.fieldnames]
    field_map = {orig: orig.strip().lower() for orig in reader.fieldnames}

    table_name = detect_table_by_headers(normalized_fieldnames)
    conn = get_db_connection()
    cursor = conn.cursor()

    rows_processed = 0
    violations = []

    try:
        conn.execute("BEGIN TRANSACTION;")
        
        for idx, raw_row in enumerate(reader, start=1):
            row = {field_map[k]: (v.strip() if v else "") for k, v in raw_row.items() if k in field_map}

            if table_name == 'students':
                sid = row.get('student_id')
                name = row.get('name')
                programme = row.get('programme', 'General')
                batch = row.get('batch', '2024')
                email = row.get('email', f"{sid}@university.edu")
                gpa = float(row.get('gpa', 0.0)) if row.get('gpa') else 0.0

                if not sid or not name:
                    violations.append(f"Row {idx}: Missing student_id or name.")
                    continue

                cursor.execute('''
                    INSERT INTO students (student_id, name, programme, batch, email, gpa)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id) DO UPDATE SET
                        name=excluded.name,
                        programme=excluded.programme,
                        batch=excluded.batch,
                        email=excluded.email,
                        gpa=excluded.gpa
                ''', (sid, name, programme, batch, email, gpa))
                rows_processed += 1

            elif table_name == 'courses':
                ccode = row.get('course_code')
                title = row.get('title')
                credits = int(row.get('credits', 3)) if row.get('credits') else 3
                semester = row.get('semester', 'Spring 2026')
                prereq = row.get('prerequisites', 'NONE')

                if not ccode or not title:
                    violations.append(f"Row {idx}: Missing course_code or title.")
                    continue

                cursor.execute('''
                    INSERT INTO courses (course_code, title, credits, semester, prerequisites)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(course_code) DO UPDATE SET
                        title=excluded.title,
                        credits=excluded.credits,
                        semester=excluded.semester,
                        prerequisites=excluded.prerequisites
                ''', (ccode, title, credits, semester, prereq))
                rows_processed += 1

            elif table_name == 'attendance':
                sid = row.get('student_id')
                ccode = row.get('course_code')
                try:
                    pct = float(row.get('attendance_pct', 0.0))
                except ValueError:
                    violations.append(f"Row {idx}: Invalid attendance percentage '{row.get('attendance_pct')}'.")
                    continue

                if not sid or not ccode:
                    violations.append(f"Row {idx}: Missing student_id or course_code.")
                    continue

                cursor.execute('''
                    INSERT INTO attendance (student_id, course_code, attendance_pct)
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id, course_code) DO UPDATE SET
                        attendance_pct=excluded.attendance_pct
                ''', (sid, ccode, pct))
                rows_processed += 1

            elif table_name == 'results':
                sid = row.get('student_id')
                ccode = row.get('course_code')
                marks = float(row.get('marks', 0.0)) if row.get('marks') else 0.0
                grade = row.get('grade', 'P')
                etype = row.get('exam_type', 'Regular')

                if not sid or not ccode:
                    violations.append(f"Row {idx}: Missing student_id or course_code.")
                    continue

                cursor.execute('''
                    INSERT INTO results (student_id, course_code, marks, grade, exam_type)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, course_code, exam_type) DO UPDATE SET
                        marks=excluded.marks,
                        grade=excluded.grade
                ''', (sid, ccode, marks, grade, etype))
                rows_processed += 1

        conn.commit()
        return {
            "status": "success",
            "target_table": table_name,
            "rows_processed": rows_processed,
            "violations_count": len(violations),
            "violations_report": violations
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": f"Transactional rollback triggered due to exception: {str(e)}",
            "violations_report": violations
        }
    finally:
        conn.close()
