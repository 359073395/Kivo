#!/usr/bin/env python3
"""Locate external HeyGen task state without storing task data in this skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path.home() / ".codex" / "tiktok-video-workflow" / "config.json"
SKILLS_ROOT = Path.home() / ".codex" / "skills"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def reject_skill_path(path: Path) -> None:
    if is_within(path, SKILLS_ROOT):
        raise ValueError("Task/output paths must not be inside the Codex skills directory.")


def default_root() -> Path:
    return Path("D:/TikTok视频生产") if Path("D:/").exists() else Path.home() / "TikTok视频生产"


def resolve_root(explicit: str | None) -> tuple[Path, str]:
    if explicit:
        root, source = Path(explicit).expanduser(), "explicit"
    elif CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        root, source = Path(config["output_root"]).expanduser(), "config"
    else:
        root, source = default_root(), "default"
    root = root.resolve()
    reject_skill_path(root)
    return root, source


def configure(path_value: str) -> dict:
    root = Path(path_value).expanduser().resolve()
    reject_skill_path(root)
    root.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "output_root": str(root),
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    temp = CONFIG_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, CONFIG_PATH)
    return {"config_path": str(CONFIG_PATH), **payload}


def locate(root: Path, skill: str) -> list[dict]:
    if not root.exists():
        return []
    matches = []
    for path in root.rglob("ACTIVE_TASK.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("skill") != skill:
            continue
        if data.get("batch_status") in {"completed", "stopped"}:
            continue
        matches.append(
            {
                "task_dir": str(path.parent),
                "sku": data.get("original_sku"),
                "batch_status": data.get("batch_status"),
                "current_index": data.get("current_index"),
                "updated_at": data.get("updated_at"),
            }
        )
    return sorted(matches, key=lambda item: item.get("updated_at") or "", reverse=True)


def check(task_value: str) -> dict:
    task_dir = Path(task_value).expanduser().resolve()
    reject_skill_path(task_dir)
    manifest = task_dir / "ACTIVE_TASK.json"
    if not task_dir.is_dir():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")
    if not manifest.is_file():
        raise FileNotFoundError(f"ACTIVE_TASK.json not found: {manifest}")
    return {
        "task_dir": str(task_dir),
        "manifest": json.loads(manifest.read_text(encoding="utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("--output-root")
    configure_cmd = sub.add_parser("configure")
    configure_cmd.add_argument("output_root")
    locate_cmd = sub.add_parser("locate")
    locate_cmd.add_argument("--skill", default="heygen-video-producer")
    locate_cmd.add_argument("--output-root")
    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("task_dir")
    args = parser.parse_args()
    try:
        if args.command == "resolve":
            root, source = resolve_root(args.output_root)
            payload = {"output_root": str(root), "source": source}
        elif args.command == "configure":
            payload = configure(args.output_root)
        elif args.command == "locate":
            root, _ = resolve_root(args.output_root)
            payload = locate(root, args.skill)
        else:
            payload = check(args.task_dir)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
