"""Lightweight metadata registry for uploaded documents.

Documents are keyed by a generated UUID (document_id), never by filename,
so two uploads with the same original filename never collide. Metadata is
persisted as a single JSON file — enough for a portfolio-scale project
without pulling in a real database.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

REGISTRY_PATH = Path("app/data/documents.json")
_lock = Lock()


def _load() -> dict:
    if not REGISTRY_PATH.exists():
        return {}

    content = REGISTRY_PATH.read_text(encoding="utf-8").strip()
    if not content:
        return {}

    return json.loads(content)


def _save(data: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def create_document(filename: str) -> dict:
    document_id = str(uuid.uuid4())

    record = {
        "document_id": document_id,
        "filename": filename,
        "upload_time": datetime.now(timezone.utc).isoformat(),
        "status": "uploaded",
        "chunk_count": 0,
        "error": None,
    }

    with _lock:
        data = _load()
        data[document_id] = record
        _save(data)

    return record


def update_document(document_id: str, **fields) -> dict:
    with _lock:
        data = _load()

        if document_id not in data:
            raise KeyError(document_id)

        data[document_id].update(fields)
        _save(data)

        return data[document_id]


def get_document(document_id: str) -> Optional[dict]:
    return _load().get(document_id)


def list_documents() -> list[dict]:
    data = _load()
    return sorted(
        data.values(),
        key=lambda record: record["upload_time"],
        reverse=True,
    )


def delete_document(document_id: str) -> None:
    with _lock:
        data = _load()
        data.pop(document_id, None)
        _save(data)
