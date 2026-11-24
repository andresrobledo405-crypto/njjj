import sqlite3
from collections.abc import Generator

from .config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rut TEXT UNIQUE,
    birth_date TEXT,
    phone TEXT,
    email TEXT,
    insurance TEXT,
    allergies TEXT,
    occupation TEXT,
    history TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS professionals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    professional_id INTEGER NOT NULL,
    starts_at TEXT NOT NULL,
    duration_min INTEGER NOT NULL DEFAULT 30,
    room TEXT,
    reason TEXT,
    plan_id INTEGER REFERENCES treatment_plans(id),
    status TEXT NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'arrived', 'done', 'cancelled', 'no_show')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (professional_id) REFERENCES professionals(id)
);
CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    professional_id INTEGER NOT NULL,
    appointment_id INTEGER,
    diagnosis TEXT,
    treatment TEXT,
    notes TEXT,
    attachment_path TEXT,
    plan_id INTEGER REFERENCES treatment_plans(id),
    eva INTEGER CHECK (eva IS NULL OR (eva >= 0 AND eva <= 10)),
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (professional_id) REFERENCES professionals(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    appointment_id INTEGER,
    concept TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    method TEXT NOT NULL DEFAULT 'cash'
        CHECK (method IN ('cash', 'card', 'transfer', 'insurance')),
    paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'profesional' CHECK (role IN ('admin', 'profesional')),
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS library_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    region TEXT,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    precautions TEXT,
    tags TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (category, title)
);
CREATE TABLE IF NOT EXISTS treatment_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    professional_id INTEGER REFERENCES professionals(id),
    title TEXT NOT NULL,
    reason TEXT,
    kine_diagnosis TEXT,
    total_sessions INTEGER NOT NULL CHECK (total_sessions >= 1 AND total_sessions <= 100),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT '°'
);
CREATE TABLE IF NOT EXISTS consultation_library (
    consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    library_item_id INTEGER NOT NULL REFERENCES library_items(id) ON DELETE RESTRICT,
    PRIMARY KEY (consultation_id, library_item_id)
);
CREATE TABLE IF NOT EXISTS exercise_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS exercise_template_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL REFERENCES exercise_templates(id) ON DELETE CASCADE,
    library_item_id INTEGER NOT NULL REFERENCES library_items(id) ON DELETE RESTRICT,
    dosage TEXT,
    notes TEXT,
    position INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_appointments_plan ON appointments(plan_id);
CREATE INDEX IF NOT EXISTS idx_consultations_plan ON consultations(plan_id);
CREATE INDEX IF NOT EXISTS idx_measurements_consultation ON measurements(consultation_id);
CREATE INDEX IF NOT EXISTS idx_conslib_item ON consultation_library(library_item_id);
CREATE INDEX IF NOT EXISTS idx_tplitems_template ON exercise_template_items(template_id);
CREATE INDEX IF NOT EXISTS idx_appointments_starts_at ON appointments(starts_at);
CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations(patient_id);
"""


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


MIGRATIONS = (
    ("patients", "occupation", "TEXT"),
    ("patients", "history", "TEXT"),
    ("appointments", "plan_id", "INTEGER REFERENCES treatment_plans(id)"),
    ("consultations", "plan_id", "INTEGER REFERENCES treatment_plans(id)"),
    ("consultations", "eva", "INTEGER CHECK (eva IS NULL OR (eva >= 0 AND eva <= 10))"),
)


def _migrate(connection: sqlite3.Connection) -> None:
    """Agrega columnas nuevas a bases creadas por versiones anteriores."""
    for table, column, definition in MIGRATIONS:
        if column not in {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    connection = get_connection()
    try:
        connection.executescript(SCHEMA)
        _migrate(connection)
        connection.commit()
    finally:
        connection.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
