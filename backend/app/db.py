"""SQLite connection and Annex C/B/D schema management."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(os.getenv("DB_PATH", "university.db"))


def get_conn(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a configured SQLite connection with FK enforcement enabled."""
    if db_path == ":memory:":
        conn = sqlite3.connect(":memory:")
    else:
        path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path | sqlite3.Connection | None = None) -> None:
    """Create tables in a database path or an already-open connection."""
    schema = """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY CHECK(student_id GLOB 'S[0-9][0-9][0-9][0-9]'),
        full_name TEXT NOT NULL,
        programme TEXT NOT NULL,
        batch_year INTEGER NOT NULL,
        current_semester INTEGER NOT NULL CHECK(current_semester BETWEEN 1 AND 10),
        cgpa REAL NOT NULL CHECK(cgpa BETWEEN 0 AND 10),
        active_backlogs INTEGER NOT NULL CHECK(active_backlogs >= 0)
    );
    CREATE TABLE IF NOT EXISTS courses (
        course_code TEXT PRIMARY KEY,
        course_name TEXT NOT NULL,
        programme TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS attendance (
        student_id TEXT NOT NULL REFERENCES students(student_id),
        course_code TEXT NOT NULL REFERENCES courses(course_code),
        classes_held INTEGER NOT NULL CHECK(classes_held > 0),
        classes_attended INTEGER NOT NULL CHECK(classes_attended >= 0 AND classes_attended <= classes_held),
        PRIMARY KEY(student_id, course_code)
    );
    CREATE TABLE IF NOT EXISTS results (
        student_id TEXT NOT NULL REFERENCES students(student_id),
        course_code TEXT NOT NULL REFERENCES courses(course_code),
        exam_session TEXT NOT NULL,
        exam_type TEXT NOT NULL CHECK(exam_type IN ('REGULAR','SUPPLEMENTARY')),
        internal_marks REAL NOT NULL CHECK(internal_marks >= 0),
        external_marks REAL NOT NULL CHECK(external_marks >= 0),
        total_marks REAL NOT NULL CHECK(total_marks = internal_marks + external_marks),
        max_marks REAL NOT NULL CHECK(max_marks > 0 AND internal_marks + external_marks <= max_marks),
        result TEXT NOT NULL CHECK(result IN ('PASS','FAIL','ABSENT','DETAINED')),
        PRIMARY KEY(student_id, course_code, exam_session, exam_type)
    );
    CREATE TABLE IF NOT EXISTS rule_registry (
        rule_id TEXT PRIMARY KEY, description TEXT, parameter TEXT, operator TEXT, value TEXT,
        scope_programmes TEXT, scope_batches TEXT, effective_from TEXT, effective_to TEXT,
        source_doc_id TEXT, source_section TEXT
    );
    CREATE TABLE IF NOT EXISTS source_register (
        doc_id TEXT PRIMARY KEY, title TEXT, issuer TEXT, authority_level INTEGER CHECK(authority_level BETWEEN 1 AND 5),
        doc_type TEXT, version TEXT, effective_from TEXT, effective_to TEXT, supersedes TEXT,
        scope_programmes TEXT, scope_batches TEXT, provenance TEXT, retrieved_on TEXT, synthetic INTEGER
    );
    CREATE TABLE IF NOT EXISTS audit_log (
        trace_id TEXT PRIMARY KEY, student_id TEXT, timestamp TEXT, record_json TEXT
    );
    """
    if isinstance(db_path, sqlite3.Connection):
        db_path.executescript(schema)
    else:
        with get_conn(db_path) as conn:
            conn.executescript(schema)
