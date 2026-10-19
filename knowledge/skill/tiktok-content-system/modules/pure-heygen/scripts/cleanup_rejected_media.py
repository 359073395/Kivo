#!/usr/bin/env python3
"""Delete rejected/generated media while preserving exact approved images and source assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


APPROVED_STATUS = "user_approved_exact_file"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
INTERMEDIATE_MARKERS = (
    "商品锁定透明层",
    "商品裁剪预览",
    "商品主体",
    "抠图坐标参考",
    "主体居中_原像素",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def under(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def approved_files(task_root: Path, manifest: dict[str, Any]) -> set[Path]:
    result: set[Path] = set()
    approval = manifest.get("exact_presenter_reapproval") or {}
    for item in approval.get("candidates") or []:
        if item.get("status") != APPROVED_STATUS:
            continue
        path = Path(str(item.get("path") or ""))
        expected_hash = str(item.get("sha256") or "").casefold()
        if not under(task_root, path) or not path.is_file():
            raise RuntimeError(f"Approved image is missing or outside task root: {path}")
        if not expected_hash or sha256_file(path).casefold() != expected_hash:
            raise RuntimeError(f"Approved image hash mismatch: {path}")
        result.add(path.resolve())
    if not result:
        raise RuntimeError("No exact approved presenter images found; refusing cleanup")
    return result


def collect(task_root: Path, manifest: dict[str, Any]) -> tuple[set[Path], set[Path]]:
    keep = approved_files(task_root, manifest)
    files: set[Path] = set()
    dirs: set[Path] = set()

    # Presenter-generation folders keep only exact approved files.
    for directory in task_root.glob("*/06_人物与商品合成"):
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.resolve() not in keep:
                files.add(path.resolve())
            elif path.is_dir():
                dirs.add(path.resolve())

    # Generated product-processing intermediates are disposable; source images remain.
    for directory in task_root.glob("*/01_产品资料"):
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and any(marker in path.name for marker in INTERMEDIATE_MARKERS):
                files.add(path.resolve())

    # Remove only remote outputs explicitly marked invalid/rejected in the task state.
    for item in manifest.get("items") or []:
        status = str(item.get("status") or "").casefold()
        if not any(marker in status for marker in ("invalid", "reject", "failed")):
            continue
        for key in ("output_path", "final_output_path"):
            path = Path(str(item.get(key) or ""))
            if path.is_file() and under(task_root, path):
                files.add(path.resolve())
            if path.name:
                qa_dir = path.with_name(path.stem + "_QA帧")
                if qa_dir.is_dir() and under(task_root, qa_dir):
                    dirs.add(qa_dir.resolve())

    return files, dirs


def execute(task_root: Path, files: set[Path], dirs: set[Path]) -> dict[str, Any]:
    removed_files = 0
    removed_bytes = 0
    for path in sorted(files):
        if path.is_file() and under(task_root, path):
            removed_bytes += path.stat().st_size
            path.unlink()
            removed_files += 1
    for path in sorted(dirs, key=lambda value: len(value.parts), reverse=True):
        if path.is_dir() and under(task_root, path):
            shutil.rmtree(path)
    return {"removed_files": removed_files, "removed_bytes": removed_bytes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_root")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    task_root = Path(args.task_root).resolve()
    if not task_root.is_dir() or task_root == Path(task_root.anchor):
        raise RuntimeError(f"Unsafe or missing task root: {task_root}")
    state_path = task_root / "ACTIVE_TASK.json"
    manifest = json.loads(state_path.read_text(encoding="utf-8-sig"))
    files, dirs = collect(task_root, manifest)
    result: dict[str, Any] = {
        "task_root": str(task_root),
        "mode": "apply" if args.apply else "dry_run",
        "candidate_files": len(files),
        "candidate_bytes": sum(path.stat().st_size for path in files if path.is_file()),
        "candidate_directories": len(dirs),
    }
    if args.apply:
        result.update(execute(task_root, files, dirs))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
