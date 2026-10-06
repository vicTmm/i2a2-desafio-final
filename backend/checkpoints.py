"""Resultados locais por bloco; conteúdo e configuração determinam a chave."""
import hashlib
import json
import os
import tempfile
from . import storage

def key(pages, prompt, schema, models):
    payload = json.dumps(["chunks-v1", pages, prompt, schema, models], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()

def load(item_key):
    path = storage.root() / "checkpoints" / (item_key + ".json")
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None

def save(item_key, value):
    folder = storage.root() / "checkpoints"
    folder.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=folder, suffix=".tmp", delete=False) as file:
        json.dump(value, file, ensure_ascii=False)
        temporary = file.name
    try:
        os.replace(temporary, folder / (item_key + ".json"))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
