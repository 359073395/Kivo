"""Embedded-Python entry point. No global Python or AI client is needed."""
from pathlib import Path
import os
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.chdir(root)
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import uvicorn

from lingxi.knowledge import get_store
store = get_store()
if (store.vault / "knowledge-base.json").is_file() and not store.db.is_file():
    store.rebuild()

uvicorn.run("web.app:app", host="127.0.0.1", port=int(os.environ["EASEL_PORT"]))
