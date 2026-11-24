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
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL DEFAULT 'protocolo',
    title TEXT NOT NULL UNIQUE,
    content TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_appointments_starts_at ON appointments(starts_at);
CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations(patient_id);
"""


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    connection = get_connection()
    try:
        connection.executescript(SCHEMA)
        connection.execute("DROP TABLE IF EXISTS library_items")  # migración: módulo anterior ya no existe
        connection.commit()
    finally:
        connection.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
