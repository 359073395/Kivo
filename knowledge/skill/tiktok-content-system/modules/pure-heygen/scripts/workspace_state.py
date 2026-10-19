#!/usr/bin/env python3
"""Recover and plan pure-HeyGen work from portable knowledge and local state."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from remote_input_gate import (  # noqa: E402
    cross_sku_remote_binding_conflicts,
    evaluate_post_render,
    evaluate_pre_submit,
)

SKILLS_ROOT = Path.home() / ".codex" / "skills"
FINISHED_BATCH_STATES = {"completed", "stopped", "archived"}
APPROVED_VALUES = {"approved", "passed", "user_approved"}


def is_finished_batch_state(value: object) -> bool:
    state = str(value or "").casefold()
    return any(state.startswith(prefix) for prefix in FINISHED_BATCH_STATES)


def marker_root(candidate: Path) -> Path | None:
    candidate = candidate.expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "knowledge-base.json").is_file():
            return path
    return None


def find_vault_root() -> Path:
    candidates: list[Path] = [Path(__file__).resolve(), Path.cwd().resolve()]
    configured = os.environ.get("KNOWLEDGE_BASE_ROOT", "").strip()
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path("D:/Knowledge"))
    for candidate in candidates:
        root = marker_root(candidate)
        if root is not None:
            return root
    raise FileNotFoundError(
        "knowledge-base.json was not found from the task path, resolved Skill path, "
        "KNOWLEDGE_BASE_ROOT, or D:\\Knowledge"
    )


VAULT_ROOT = find_vault_root()
CONFIG_PATH = VAULT_ROOT / "辅助" / "配置" / "machine-paths.local.json"

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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_root(explicit: str | None) -> tuple[Path, str]:
    if explicit:
        root, source = Path(explicit).expanduser(), "explicit"
    elif os.environ.get("PRODUCTION_WORK_ROOT", "").strip():
        root, source = Path(os.environ["PRODUCTION_WORK_ROOT"]).expanduser(), "environment"
    elif CONFIG_PATH.exists():
        config = read_json(CONFIG_PATH)
        configured = str(config.get("productionWorkRoot") or "").strip()
        if not configured:
            raise ValueError("productionWorkRoot is blank in machine-paths.local.json")
        root, source = Path(configured).expanduser(), "machine-paths.local.json"
    else:
        raise FileNotFoundError(
            "machine-paths.local.json is missing; provide --output-root explicitly"
        )
    root = root.resolve()
    reject_skill_path(root)
    return root, source


def configure(path_value: str) -> dict[str, Any]:
    root = Path(path_value).expanduser().resolve()
    reject_skill_path(root)
    root.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {}
    if CONFIG_PATH.is_file():
        payload = read_json(CONFIG_PATH)
    payload["productionWorkRoot"] = str(root)
    payload["updatedAt"] = datetime.now().astimezone().isoformat(timespec="seconds")
    temp = CONFIG_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, CONFIG_PATH)
    return {
        "config_path": str(CONFIG_PATH),
        "productionWorkRoot": str(root),
        "updatedAt": payload["updatedAt"],
    }


def normalize_task_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def unique_near_match(requested: Path) -> tuple[Path | None, list[Path]]:
    parent = requested.parent
    if not parent.is_dir():
        return None, []
    wanted = normalize_task_name(requested.name)
    matches = [
        child
        for child in parent.iterdir()
        if child.is_dir() and normalize_task_name(child.name) == wanted
    ]
    matches.sort(key=lambda path: path.name.casefold())
    return (matches[0] if len(matches) == 1 else None), matches


def manifest_candidate(path: Path, source: str, summary_path: Path | None = None) -> dict[str, Any] | None:
    manifest_path = path / "ACTIVE_TASK.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError):
        return None
    if manifest.get("skill") != "tiktok-content-system":
        return None
    if manifest.get("mode") not in {None, "pure_heygen"}:
        return None
    if is_finished_batch_state(manifest.get("batch_status")):
        return None
    return {
        "task_dir": str(path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "source": source,
        "project_summary": str(summary_path.resolve()) if summary_path else None,
        "task_id": manifest.get("task_id"),
        "batch_status": manifest.get("batch_status"),
        "current_index": manifest.get("current_index"),
        "updated_at": manifest.get("updated_at"),
    }


def locate(root: Path, skill: str = "tiktok-content-system") -> list[dict[str, Any]]:
    if not root.exists():
        return []
    matches: list[dict[str, Any]] = []
    for manifest_path in root.rglob("ACTIVE_TASK.json"):
        try:
            data = read_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("skill") != skill:
            continue
        if data.get("mode") not in {None, "pure_heygen"}:
            continue
        if is_finished_batch_state(data.get("batch_status")):
            continue
        matches.append(
            {
                "task_dir": str(manifest_path.parent.resolve()),
                "manifest_path": str(manifest_path.resolve()),
                "source": "production-root-scan",
                "project_summary": None,
                "task_id": data.get("task_id"),
                "batch_status": data.get("batch_status"),
                "current_index": data.get("current_index"),
                "updated_at": data.get("updated_at"),
            }
        )
    return sorted(matches, key=lambda item: item.get("updated_at") or "", reverse=True)


def project_summary_candidates() -> list[dict[str, Any]]:
    project_root = VAULT_ROOT / "项目" / "进行中"
    if not project_root.is_dir():
        return []
    candidates: list[dict[str, Any]] = []
    path_pattern = re.compile(r"(?:外部生产目录|运行状态源)：`([^`]+)`")
    for summary in project_root.glob("*.md"):
        try:
            text = summary.read_text(encoding="utf-8")
        except OSError:
            continue
        for raw_value in path_pattern.findall(text):
            value = Path(raw_value)
            task_dir = value.parent if value.name.casefold() == "active_task.json" else value
            candidate = manifest_candidate(task_dir, "project-summary", summary)
            if candidate:
                candidates.append(candidate)
                break
    return candidates


def deduplicate_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        key = os.path.normcase(candidate["task_dir"])
        current = by_path.get(key)
        if current is None or candidate["source"] == "project-summary":
            by_path[key] = candidate
    return list(by_path.values())


def sample_is_approved(manifest: dict[str, Any], summary_text: str = "") -> bool:
    sample = manifest.get("sample_approval")
    if isinstance(sample, dict) and str(sample.get("status") or "").casefold() in APPROVED_VALUES:
        return True
    for item in manifest.get("items") or []:
        if isinstance(item, dict) and str(item.get("user_approval") or "").casefold() == "approved":
            return True
    return "样片批准：`approved`" in summary_text


def approval_time_key(record: dict[str, Any]) -> tuple[datetime, str]:
    raw_value = str(record.get("approved_at") or "")
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.astimezone()
    except ValueError:
        parsed = datetime.min.astimezone()
    return parsed, str(record.get("standard_id") or record.get("version") or "")


def select_latest_batch_standard(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    approved: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        status = str(record.get("status") or "").casefold()
        batch_authorized = bool(record.get("batch_authorized")) or str(
            record.get("approval_kind") or ""
        ).casefold() == "batch_execution"
        if status.startswith("approved"):
            batch_authorized = True
        if status not in {"active", "approved", "approved_in_current_run"}:
            continue
        if not batch_authorized:
            continue
        approved.append(record)
    return max(approved, key=approval_time_key) if approved else None


def batch_standard_from_manifest(manifest: dict[str, Any]) -> dict[str, Any] | None:
    records = [
        record
        for record in (manifest.get("standard_history") or [])
        if isinstance(record, dict)
    ]
    active_standard = manifest.get("active_standard")
    if isinstance(active_standard, dict):
        records.append(active_standard)
    batch_approval = manifest.get("batch_approval")
    if isinstance(batch_approval, dict):
        records.append(
            {
                **batch_approval,
                "standard_id": batch_approval.get("standard_id")
                or manifest.get("active_standard_id"),
                "batch_authorized": str(batch_approval.get("status") or "").casefold()
                == "approved",
                "method_id": manifest.get("method_id"),
                "method_version": manifest.get("method_version"),
            }
        )
    legacy = manifest.get("batch_authorization")
    if isinstance(legacy, dict):
        records.append(
            {
                "standard_id": manifest.get("active_standard_id")
                or legacy.get("approved_sample_task_id"),
                "status": legacy.get("status"),
                "batch_authorized": str(legacy.get("status") or "")
                .casefold()
                .startswith("approved"),
                "approved_at": legacy.get("approved_at"),
                "approved_sample_task_id": legacy.get("approved_sample_task_id"),
                "method_id": manifest.get("method_id") or "M-CNT-PURE-HEYGEN-001",
                "method_version": manifest.get("method_version"),
            }
        )
    return select_latest_batch_standard(records)


def decide_next_action(
    *,
    has_product: bool,
    has_approved_script_or_audio: bool,
    presenter_state: str,
    sample_approved: bool,
    batch_approved: bool,
    batch_status: str,
) -> str:
    lowered_status = batch_status.casefold()
    if any(token in lowered_status for token in ("quota", "credit", "额度")):
        return "blocked_external_quota"
    if not has_product:
        return "stop_missing_product"
    if not has_approved_script_or_audio:
        return "stop_missing_approved_script_or_audio"
    if presenter_state == "missing":
        return "prepare_one_presenter_candidate"
    if presenter_state not in APPROVED_VALUES:
        return "await_presenter_approval"
    if not sample_approved:
        return "generate_one_video_sample"
    if not batch_approved:
        return "await_batch_approval"
    return "continue_serial_batch"


def first_actionable_item(manifest: dict[str, Any]) -> dict[str, Any] | None:
    terminal_prefixes = ("completed", "ready_to_publish", "skipped", "rejected", "superseded")
    for item in manifest.get("items") or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "pending").casefold()
        if not status.startswith(terminal_prefixes):
            return item
    next_item = manifest.get("next_item")
    return next_item if isinstance(next_item, dict) else None


def first_completed_binding_issue(manifest: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    for item in manifest.get("items") or []:
        if not isinstance(item, dict):
            continue
        if not str(item.get("status") or "").casefold().startswith("completed"):
            continue
        result = evaluate_post_render(item)
        if not result.get("approved"):
            return item, result
    return None, None


def path_field_exists(item: dict[str, Any], fields: tuple[str, ...]) -> bool:
    for field in fields:
        raw_value = item.get(field)
        if raw_value and Path(str(raw_value)).is_file():
            return True
    return False


def plan_task(task_dir: Path, summary_path: Path | None = None) -> dict[str, Any]:
    manifest_path = task_dir / "ACTIVE_TASK.json"
    manifest = read_json(manifest_path)
    summary_text = ""
    if summary_path and summary_path.is_file():
        summary_text = summary_path.read_text(encoding="utf-8")
    approved = sample_is_approved(manifest, summary_text)
    batch_standard = batch_standard_from_manifest(manifest)
    batch_approved = batch_standard is not None
    batch_status = str(manifest.get("batch_status") or "")
    binding_conflicts = cross_sku_remote_binding_conflicts(
        [item for item in (manifest.get("items") or []) if isinstance(item, dict)]
    )
    gate_reasons: list[str] = []
    if binding_conflicts:
        action = "stop_cross_sku_remote_avatar_reuse"
        item = None
        gate_reasons = ["one_remote_avatar_or_asset_id_is_bound_to_multiple_skus"]
    elif any(token in batch_status.casefold() for token in ("invalidated", "rework_blocked")):
        action = "await_presenter_reapproval"
        item = first_actionable_item(manifest)
        gate_reasons = ["batch_invalidated_after_remote_input_or_render_mismatch"]
    elif any(token in batch_status.casefold() for token in ("quota", "credit", "额度")):
        action = "blocked_external_quota"
        item = None
    else:
        completed_issue_item, completed_issue = first_completed_binding_issue(manifest)
        if completed_issue_item is not None and completed_issue is not None:
            item = completed_issue_item
            action = str(completed_issue["action"])
            gate_reasons = [str(reason) for reason in completed_issue.get("reasons") or []]
        else:
            item = first_actionable_item(manifest)
        if completed_issue_item is None and item is None:
            remaining_count = int((manifest.get("credit_blocker") or {}).get("remaining_video_count") or 0)
            action = (
                "continue_serial_batch"
                if approved and batch_approved and remaining_count > 0
                else "await_batch_approval"
                if approved and not batch_approved
                else "inspect_execution_table"
            )
        elif completed_issue_item is None:
            has_product = path_field_exists(
                item,
                ("product_source_path", "product_image", "white_background_product_image"),
            ) or bool(item.get("product_visual_qc", {}).get("source_layer_locked"))
            has_audio = path_field_exists(item, ("audio_path",)) or bool(item.get("script"))
            presenter_path_exists = path_field_exists(item, ("presenter_image",))
            presenter_qc = str(item.get("presenter_qc_status") or "").casefold()
            if presenter_qc not in APPROVED_VALUES:
                if item.get("persona_qc", {}).get("passed") and item.get("product_visual_qc", {}).get("passed"):
                    presenter_qc = "passed"
                elif presenter_path_exists:
                    presenter_qc = "present_unapproved"
                else:
                    presenter_qc = "missing"
            if presenter_qc in APPROVED_VALUES:
                binding_result = evaluate_pre_submit(item)
            else:
                binding_result = None
            if binding_result is not None and not binding_result.get("approved"):
                action = str(binding_result["action"])
                gate_reasons = [str(reason) for reason in binding_result.get("reasons") or []]
            else:
                action = decide_next_action(
                    has_product=has_product,
                    has_approved_script_or_audio=has_audio,
                    presenter_state=presenter_qc,
                    sample_approved=approved,
                    batch_approved=batch_approved,
                    batch_status=batch_status,
                )
    return {
        "task_dir": str(task_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "task_id": manifest.get("task_id"),
        "batch_status": batch_status,
        "sample_approved": approved,
        "batch_approved": batch_approved,
        "active_standard_id": batch_standard.get("standard_id") if batch_standard else None,
        "next_action": action,
        "next_item_task_id": item.get("task_id") if item else None,
        "method_id": "M-CNT-PURE-HEYGEN-001",
        "gate_reasons": gate_reasons,
        "remote_binding_conflicts": binding_conflicts,
    }


def recover(task_value: str | None, output_root: str | None) -> dict[str, Any]:
    if task_value:
        requested = Path(task_value).expanduser()
        if requested.is_dir():
            task_dir = requested.resolve()
            source = "explicit"
            alternatives: list[Path] = []
        else:
            task_dir, alternatives = unique_near_match(requested)
            if task_dir is None:
                return {
                    "vault_root": str(VAULT_ROOT),
                    "status": "not_found_or_ambiguous",
                    "requested": str(requested),
                    "candidates": [str(path.resolve()) for path in alternatives],
                    "must_not_create_duplicate": True,
                }
            source = "unique-normalized-near-match"
        checked = manifest_candidate(task_dir, source)
        if checked is None:
            raise FileNotFoundError(f"ACTIVE_TASK.json not found or not pure HeyGen: {task_dir}")
        checked["status"] = "recovered"
        checked["vault_root"] = str(VAULT_ROOT)
        checked["plan"] = plan_task(task_dir)
        return checked

    summary_candidates = deduplicate_candidates(project_summary_candidates())
    candidates = summary_candidates
    if not candidates:
        root, _ = resolve_root(output_root)
        candidates = deduplicate_candidates(locate(root))
    if len(candidates) != 1:
        return {
            "vault_root": str(VAULT_ROOT),
            "status": "needs_selection" if candidates else "not_found",
            "candidates": candidates,
            "must_not_create_duplicate": True,
        }
    result = candidates[0]
    summary_path = Path(result["project_summary"]) if result.get("project_summary") else None
    result["status"] = "recovered"
    result["vault_root"] = str(VAULT_ROOT)
    result["plan"] = plan_task(Path(result["task_dir"]), summary_path)
    return result


def check(task_value: str) -> dict[str, Any]:
    task_dir = Path(task_value).expanduser().resolve()
    reject_skill_path(task_dir)
    manifest = task_dir / "ACTIVE_TASK.json"
    if not task_dir.is_dir():
        raise FileNotFoundError(f"Task directory not found: {task_dir}")
    if not manifest.is_file():
        raise FileNotFoundError(f"ACTIVE_TASK.json not found: {manifest}")
    return {"task_dir": str(task_dir), "manifest": read_json(manifest), "plan": plan_task(task_dir)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    resolve = sub.add_parser("resolve")
    resolve.add_argument("--output-root")
    configure_cmd = sub.add_parser("configure")
    configure_cmd.add_argument("output_root")
    locate_cmd = sub.add_parser("locate")
    locate_cmd.add_argument("--skill", default="tiktok-content-system")
    locate_cmd.add_argument("--output-root")
    recover_cmd = sub.add_parser("recover")
    recover_cmd.add_argument("--task-dir")
    recover_cmd.add_argument("--output-root")
    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("task_dir")
    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("task_dir")
    args = parser.parse_args()
    try:
        if args.command == "resolve":
            root, source = resolve_root(args.output_root)
            payload: Any = {"vault_root": str(VAULT_ROOT), "output_root": str(root), "source": source}
        elif args.command == "configure":
            payload = configure(args.output_root)
        elif args.command == "locate":
            root, _ = resolve_root(args.output_root)
            payload = locate(root, args.skill)
        elif args.command == "recover":
            payload = recover(args.task_dir, args.output_root)
        elif args.command == "plan":
            payload = plan_task(Path(args.task_dir).expanduser().resolve())
        else:
            payload = check(args.task_dir)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
