import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

def root():
    path = Path(os.getenv("DATA_DIR", "data")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

@contextmanager
def connect():
    db = sqlite3.connect(root() / "insurminds.sqlite3", timeout=30)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE IF NOT EXISTS policies (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS comparisons (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    try:
        with db:
            yield db
    finally:
        db.close()

def save(table, value):
    assert table in ("policies", "comparisons")
    with connect() as db:
        db.execute(f"INSERT OR REPLACE INTO {table} VALUES (?, ?)", (value["id"], json.dumps(value, ensure_ascii=False)))

def get(table, item_id):
    assert table in ("policies", "comparisons")
    with connect() as db:
        row = db.execute(f"SELECT payload FROM {table} WHERE id=?", (item_id,)).fetchone()
    return json.loads(row[0]) if row else None

def all_items(table):
    assert table in ("policies", "comparisons")
    with connect() as db:
        rows = db.execute(f"SELECT payload FROM {table} ORDER BY rowid DESC").fetchall()
    return [json.loads(r[0]) for r in rows]
