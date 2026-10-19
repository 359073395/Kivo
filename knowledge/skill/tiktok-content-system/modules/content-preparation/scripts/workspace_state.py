#!/usr/bin/env python3
"""Resolve external output roots and maintain lightweight resumable task manifests."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def find_vault_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "knowledge-base.json").is_file():
            return parent
    raise FileNotFoundError("knowledge-base.json was not found above this script")


VAULT_ROOT = find_vault_root()
CONFIG_PATH = VAULT_ROOT / "辅助" / "配置" / "machine-paths.local.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def reject_skill_output(path: Path) -> None:
    skills_root = Path.home() / ".codex" / "skills"
    if is_within(path, SKILL_DIR) or is_within(path, skills_root):
        raise ValueError("Output/task paths must not be inside the Codex skills directory.")


def resolve_root(explicit: str | None) -> tuple[Path, str]:
    if explicit:
        root, source = Path(explicit).expanduser(), "explicit"
    elif os.environ.get("PRODUCTION_WORK_ROOT", "").strip():
        root, source = Path(os.environ["PRODUCTION_WORK_ROOT"]).expanduser(), "environment"
    elif CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        configured = str(config.get("productionWorkRoot") or "").strip()
        if not configured:
            raise ValueError(
                "productionWorkRoot is blank in machine-paths.local.json"
            )
        root, source = Path(configured).expanduser(), "machine-paths.local.json"
    else:
        raise FileNotFoundError(
            "machine-paths.local.json is missing; provide --output-root explicitly"
        )
    root = root.resolve()
    reject_skill_output(root)
    return root, source


def safe_name(value: str, fallback: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value).strip(" ._")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned or fallback)[:64]


def create_task(args: argparse.Namespace) -> dict:
    root, source = resolve_root(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    sku = safe_name(args.sku, "SKU")
    form = safe_name(args.form, "task")
    base = root / f"{sku}_{datetime.now():%Y%m%d}_{form}"
    task_dir = base
    suffix = 2
    while task_dir.exists():
        task_dir = Path(f"{base}_{suffix:02d}")
        suffix += 1
    reject_skill_output(task_dir)
    for relative in (
        "inputs",
        "images/product",
        "images/presenter",
        "images/broll_plan",
        "tables",
        "videos/raw",
        "videos/polished",
        "subtitles",
        "logs",
    ):
        (task_dir / relative).mkdir(parents=True, exist_ok=True)
    created = now_iso()
    manifest = {
        "schema_version": 1,
        "task_id": str(uuid.uuid4()),
        "skill": args.skill,
        "original_sku": args.sku,
        "safe_sku": sku,
        "mode": form,
        "created_at": created,
        "updated_at": created,
        "output_root": str(root),
        "output_root_source": source,
        "task_dir": str(task_dir),
        "rights_confirmed": False,
        "consent_confirmed": False,
        "generation_policy_checked": False,
        "generation_policy_result": "needs_review",
        "aigc_disclosure_required": True,
        "commercial_disclosure_required": True,
        "platform_scope": "tiktok_only",
        "current_index": 0,
        "batch_status": "preflight",
        "items": [],
    }
    atomic_json(task_dir / "ACTIVE_TASK.json", manifest)
    return manifest


def locate_tasks(args: argparse.Namespace) -> list[dict]:
    root, _ = resolve_root(args.output_root)
    if not root.exists():
        return []
    matches = []
    for manifest_path in root.rglob("ACTIVE_TASK.json"):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if args.skill and data.get("skill") != args.skill:
            continue
        if data.get("batch_status") in {"completed", "stopped"}:
            continue
        matches.append(
            {
                "task_dir": str(manifest_path.parent),
                "skill": data.get("skill"),
                "sku": data.get("original_sku"),
                "batch_status": data.get("batch_status"),
                "updated_at": data.get("updated_at"),
            }
        )
    return sorted(matches, key=lambda item: item.get("updated_at") or "", reverse=True)


def check_task(path_value: str) -> dict:
    task_dir = Path(path_value).expanduser().resolve()
    reject_skill_output(task_dir)
    manifest_path = task_dir / "ACTIVE_TASK.json"
    if not task_dir.is_dir():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"ACTIVE_TASK.json not found: {manifest_path}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {"task_dir": str(task_dir), "manifest": data}


def configure(path_value: str) -> dict:
    root = Path(path_value).expanduser().resolve()
    reject_skill_output(root)
    root.mkdir(parents=True, exist_ok=True)
    data = {}
    if CONFIG_PATH.is_file():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    data["productionWorkRoot"] = str(root)
    data["updatedAt"] = now_iso()
    atomic_json(CONFIG_PATH, data)
    return {
        "config_path": str(CONFIG_PATH),
        "productionWorkRoot": str(root),
        "updatedAt": data["updatedAt"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    sub = result.add_subparsers(dest="command", required=True)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("--output-root")
    configure_cmd = sub.add_parser("configure")
    configure_cmd.add_argument("output_root")
    create = sub.add_parser("create")
    create.add_argument("--skill", required=True)
    create.add_argument("--sku", required=True)
    create.add_argument("--form", required=True)
    create.add_argument("--output-root")
    locate = sub.add_parser("locate")
    locate.add_argument("--skill")
    locate.add_argument("--output-root")
    check = sub.add_parser("check")
    check.add_argument("task_dir")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "resolve":
            root, source = resolve_root(args.output_root)
            payload = {"output_root": str(root), "source": source}
        elif args.command == "configure":
            payload = configure(args.output_root)
        elif args.command == "create":
            payload = create_task(args)
        elif args.command == "locate":
            payload = locate_tasks(args)
        else:
            payload = check_task(args.task_dir)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
