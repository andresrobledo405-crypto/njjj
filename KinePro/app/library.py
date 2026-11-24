"""Carga la biblioteca de kinesiología desde library_data.txt (no sobrescribe ediciones)."""
import sqlite3
from pathlib import Path

DATA_FILE = Path(__file__).with_name("library_data.txt")
CATEGORIES = {
    "evaluacion": "Evaluación",
    "patologia": "Patologías",
    "ejercicio": "Ejercicios",
    "tecnica": "Técnicas y agentes",
    "anatomia": "Anatomía",
    "clinica": "Práctica clínica",
    "glosario": "Glosario",
}


def parse_library(text: str) -> list[dict]:
    items, current = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            category, region, title = (part.strip() for part in line[3:].split("|", 2))
            current = {"category": category, "region": region, "title": title, "summary": "", "body": [], "precautions": [], "tags": ""}
            items.append(current)
        elif current is None or not line.strip():
            continue
        elif line.startswith("> "):
            current["summary"] = line[2:].strip()
        elif line.startswith("! "):
            current["precautions"].append(line[2:].strip())
        elif line.startswith("# "):
            current["tags"] = line[2:].strip()
        else:
            current["body"].append(line.strip())
    for item in items:
        item["content"] = "\n".join(item.pop("body"))
        item["precautions"] = "\n".join(item["precautions"])
    return items


def seed_library(db: sqlite3.Connection) -> int:
    inserted = 0
    for item in parse_library(DATA_FILE.read_text(encoding="utf-8")):
        cursor = db.execute(
            """INSERT OR IGNORE INTO library_items (category, region, title, summary, content, precautions, tags)
               VALUES (:category, :region, :title, :summary, :content, :precautions, :tags)""",
            item,
        )
        inserted += cursor.rowcount
    db.commit()
    return inserted
