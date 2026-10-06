import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from backend.config import SQLITE_DB_PATH, DEFAULT_AS_OF_DATE

def get_db_connection():
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            programme TEXT NOT NULL,
            batch TEXT NOT NULL,
            email TEXT,
            gpa REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Active'
        )
    ''')

    # 2. Courses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_code TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            credits INTEGER DEFAULT 3,
            semester TEXT,
            prerequisites TEXT
        )
    ''')

    # 3. Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            student_id TEXT,
            course_code TEXT,
            attendance_pct REAL,
            PRIMARY KEY (student_id, course_code),
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            FOREIGN KEY (course_code) REFERENCES courses (course_code)
        )
    ''')

    # 4. Results Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            student_id TEXT,
            course_code TEXT,
            marks REAL,
            grade TEXT,
            exam_type TEXT DEFAULT 'Regular',
            PRIMARY KEY (student_id, course_code, exam_type),
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            FOREIGN KEY (course_code) REFERENCES courses (course_code)
        )
    ''')

    # 5. Source Register Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS source_register (
            doc_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            doc_type TEXT DEFAULT 'Circular',
            authority_level INTEGER DEFAULT 3,
            effective_from TEXT DEFAULT '2026-01-01',
            version TEXT DEFAULT '1.0',
            ingested_at TEXT
        )
    ''')

    # 6. Rule Registry Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rule_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_code TEXT NOT NULL,
            parameter TEXT NOT NULL,
            operator TEXT NOT NULL,
            value TEXT NOT NULL,
            effective_from TEXT DEFAULT '2026-01-01',
            scope_programmes TEXT DEFAULT 'ALL',
            scope_batches TEXT DEFAULT 'ALL',
            authority_level INTEGER DEFAULT 3,
            source_doc_id TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT
        )
    ''')

    # 7. Audit Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            trace_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            as_of_date TEXT NOT NULL,
            student_id TEXT,
            question_masked TEXT,
            answer_type TEXT NOT NULL,
            applied_rules TEXT,
            citations TEXT,
            tools_invoked TEXT,
            llm_call_count INTEGER DEFAULT 0,
            latency_ms REAL DEFAULT 0.0
        )
    ''')

    conn.commit()
    conn.close()
    seed_default_data()

def seed_default_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Seed Default Source Docs
    cursor.execute("SELECT COUNT(*) FROM source_register")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO source_register (doc_id, title, doc_type, authority_level, effective_from, version, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ''', [
            ('DOC-REG-2025-01', 'University General Academic Regulations 2025', 'Statute', 1, '2025-01-01', '1.0'),
            ('DOC-CIRC-2026-04', 'Attendance Threshold & Supplementary Rules Circular', 'Circular', 2, '2026-09-01', '2.0'),
            ('DOC-UNOFFICIAL-01', 'Student Council Exam FAQ & Tips', 'Guide', 5, '2026-01-01', '1.0')
        ])

    # Seed Default Rules
    cursor.execute("SELECT COUNT(*) FROM rule_registry")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO rule_registry (rule_code, parameter, operator, value, effective_from, scope_programmes, scope_batches, authority_level, source_doc_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', [
            ('R-ATT-01', 'min_attendance_pct', '>=', '75', '2025-01-01', 'ALL', 'ALL', 1, 'DOC-REG-2025-01', 'active'),
            ('R-ATT-COND-01', 'condonation_attendance_pct', 'between', '65,74', '2026-09-01', 'ALL', '2023+', 2, 'DOC-CIRC-2026-04', 'active'),
            ('R-PASS-01', 'min_pass_marks', '>=', '40', '2025-01-01', 'ALL', 'ALL', 1, 'DOC-REG-2025-01', 'active'),
            ('R-GPA-DEAN-01', 'deans_list_min_cgpa', '>=', '3.80', '2025-01-01', 'ALL', 'ALL', 1, 'DOC-REG-2025-01', 'active')
        ])

    # Seed Sample Students (including reserved judge range S9000-S9999 & Alex Mercer)
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO students (student_id, name, programme, batch, email, gpa, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('HCL2026-8891', 'Alex Mercer', 'B.Tech Computer Science & AI', '2023', 'alex.mercer@university.edu', 3.86, 'Active'),
            ('S1001', 'Priya Sharma', 'B.Tech Computer Science', '2024', 'priya.s@university.edu', 3.42, 'Active'),
            ('S9001', 'Judge Test Student 1', 'B.Tech Computer Science', '2023', 'judge9001@university.edu', 3.50, 'Active')
        ])

    # Seed Sample Courses
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO courses (course_code, title, credits, semester, prerequisites)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('CS601', 'Deep Learning & Neural Networks', 4, 'Spring 2026', 'CS501'),
            ('CS602', 'Cloud Computing & Microservices', 3, 'Spring 2026', 'CS402'),
            ('CS501', 'Artificial Intelligence Principles', 4, 'Fall 2025', 'CS401'),
            ('JDG101', 'Judge Evaluation Course I', 4, 'Spring 2026', 'NONE')
        ])

    # Seed Sample Attendance & Results
    cursor.execute("SELECT COUNT(*) FROM attendance")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO attendance (student_id, course_code, attendance_pct)
            VALUES (?, ?, ?)
        ''', [
            ('HCL2026-8891', 'CS601', 88.5),
            ('HCL2026-8891', 'CS602', 78.0),
            ('S1001', 'CS601', 68.0),
            ('S9001', 'JDG101', 72.0)
        ])

    cursor.execute("SELECT COUNT(*) FROM results")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO results (student_id, course_code, marks, grade, exam_type)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('HCL2026-8891', 'CS501', 92.0, 'A', 'Regular'),
            ('S1001', 'CS501', 58.0, 'C', 'Regular'),
            ('S9001', 'JDG101', 35.0, 'F', 'Regular')
        ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
