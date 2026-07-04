"""
SkillPilot AI — Database layer
Lightweight SQLite persistence (no ORM) so the project runs anywhere
with zero external services.
"""
import sqlite3
import json
import os
import time
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "skillpilot.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    target_role TEXT,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    raw_text TEXT,
    extracted_skills TEXT,   -- JSON list
    suggestions TEXT,        -- JSON list
    created_at REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS skill_gaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    target_role TEXT NOT NULL,
    have_skills TEXT,        -- JSON list
    missing_skills TEXT,     -- JSON list
    readiness_score INTEGER, -- 0-100
    created_at REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    target_role TEXT NOT NULL,
    roadmap_json TEXT NOT NULL,  -- full structured roadmap
    created_at REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    courses_json TEXT,
    projects_json TEXT,
    created_at REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS progress_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    week_number INTEGER,
    milestone TEXT,
    status TEXT,             -- 'pending' | 'in_progress' | 'done'
    updated_at REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value TEXT,       -- JSON
    updated_at REAL NOT NULL,
    UNIQUE(student_id, agent_name, memory_key)
);
"""


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def now():
    return time.time()


# ---------- Students ----------
def get_or_create_student(name, email, target_role=None):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE email = ?", (email,)).fetchone()
        if row:
            if target_role and target_role != row["target_role"]:
                conn.execute("UPDATE students SET target_role = ? WHERE id = ?", (target_role, row["id"]))
                conn.commit()
            return dict(conn.execute("SELECT * FROM students WHERE id = ?", (row["id"],)).fetchone())
        cur = conn.execute(
            "INSERT INTO students (name, email, target_role, created_at) VALUES (?, ?, ?, ?)",
            (name, email, target_role, now()),
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone())


def get_student(student_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict(row) if row else None


# ---------- Resumes ----------
def save_resume(student_id, filename, raw_text, extracted_skills, suggestions):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO resumes (student_id, filename, raw_text, extracted_skills, suggestions, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (student_id, filename, raw_text, json.dumps(extracted_skills), json.dumps(suggestions), now()),
        )
        conn.commit()
        return cur.lastrowid


def latest_resume(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE student_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- Skill gaps ----------
def save_skill_gap(student_id, target_role, have_skills, missing_skills, readiness_score):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO skill_gaps (student_id, target_role, have_skills, missing_skills, readiness_score, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (student_id, target_role, json.dumps(have_skills), json.dumps(missing_skills), readiness_score, now()),
        )
        conn.commit()
        return cur.lastrowid


def latest_skill_gap(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM skill_gaps WHERE student_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- Roadmaps ----------
def save_roadmap(student_id, target_role, roadmap):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO roadmaps (student_id, target_role, roadmap_json, created_at) VALUES (?, ?, ?, ?)",
            (student_id, target_role, json.dumps(roadmap), now()),
        )
        conn.commit()
        return cur.lastrowid


def latest_roadmap(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM roadmaps WHERE student_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- Recommendations ----------
def save_recommendations(student_id, courses, projects):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO recommendations (student_id, courses_json, projects_json, created_at) VALUES (?, ?, ?, ?)",
            (student_id, json.dumps(courses), json.dumps(projects), now()),
        )
        conn.commit()
        return cur.lastrowid


def latest_recommendations(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM recommendations WHERE student_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------- Progress ----------
def upsert_progress(student_id, week_number, milestone, status):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM progress_log WHERE student_id=? AND week_number=? AND milestone=?",
            (student_id, week_number, milestone),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE progress_log SET status=?, updated_at=? WHERE id=?",
                (status, now(), existing["id"]),
            )
        else:
            conn.execute(
                """INSERT INTO progress_log (student_id, week_number, milestone, status, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (student_id, week_number, milestone, status, now()),
            )
        conn.commit()


def get_progress(student_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM progress_log WHERE student_id=? ORDER BY week_number ASC", (student_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- Agent memory (long-term memory across sessions) ----------
def remember(student_id, agent_name, key, value):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO agent_memory (student_id, agent_name, memory_key, memory_value, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(student_id, agent_name, memory_key)
               DO UPDATE SET memory_value=excluded.memory_value, updated_at=excluded.updated_at""",
            (student_id, agent_name, key, json.dumps(value), now()),
        )
        conn.commit()


def recall(student_id, agent_name, key, default=None):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT memory_value FROM agent_memory WHERE student_id=? AND agent_name=? AND memory_key=?",
            (student_id, agent_name, key),
        ).fetchone()
        return json.loads(row["memory_value"]) if row else default


def recall_all(student_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT agent_name, memory_key, memory_value, updated_at FROM agent_memory WHERE student_id=?",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]
