#!/usr/bin/env python3
"""Deterministic approval, remote-input and rendered-output binding gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


APPROVED_VALUES = {"approved", "passed", "user_approved"}
EXACT_APPROVAL_SCOPE = "exact_sku_exact_file"
FRAME_POINTS = ("start", "middle", "end")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_path(value: Any) -> str:
    if value is None:
        return ""
    return os.path.normcase(os.path.abspath(os.path.expanduser(str(value))))


def _result(approved: bool, action: str, *reasons: str) -> dict[str, Any]:
    return {"approved": approved, "action": action, "reasons": list(reasons)}


def evaluate_pre_submit(item: dict[str, Any]) -> dict[str, Any]:
    """Require one exact user-approved file to be bound to one verified remote input."""

    sku = str(item.get("sku") or "").strip()
    presenter_path = str(item.get("presenter_image") or "").strip()
    presenter_sha = str(item.get("presenter_image_sha256") or "").strip().casefold()
    approval = item.get("presenter_approval") or {}

    if str(approval.get("status") or "").casefold() not in APPROVED_VALUES:
        return _result(False, "await_presenter_approval", "missing_exact_user_approval")
    if approval.get("scope") != EXACT_APPROVAL_SCOPE:
        return _result(False, "stop_approval_scope_not_exact", "approval_scope_must_be_exact_sku_exact_file")
    if str(approval.get("sku") or "").strip() != sku:
        return _result(False, "stop_approval_sku_mismatch", "approval_sku_does_not_match_item")
    if normalized_path(approval.get("approved_path")) != normalized_path(presenter_path):
        return _result(False, "stop_approved_file_mismatch", "approved_path_does_not_match_presenter_image")

    approved_sha = str(approval.get("approved_sha256") or "").strip().casefold()
    if not approved_sha or approved_sha != presenter_sha:
        return _result(False, "stop_approved_file_mismatch", "approved_sha256_does_not_match_presenter_sha256")
    if not str(approval.get("approved_version") or "").strip():
        return _result(False, "stop_approval_evidence_incomplete", "missing_approved_version")
    if not str(approval.get("approved_at") or "").strip() or not str(approval.get("evidence") or "").strip():
        return _result(False, "stop_approval_evidence_incomplete", "missing_approval_time_or_evidence")
    if str(approval.get("source_approval_type") or "").casefold() == "contextual_multi_image":
        displayed_hashes = {
            str(value).strip().casefold()
            for value in (approval.get("displayed_asset_sha256s") or [])
            if str(value).strip()
        }
        if approved_sha not in displayed_hashes:
            return _result(
                False,
                "stop_contextual_approval_asset_mismatch",
                "contextual_approval_does_not_prove_this_exact_displayed_asset",
            )

    source = Path(presenter_path)
    if not source.is_file():
        return _result(False, "stop_approved_file_missing", "approved_presenter_file_not_found")
    if sha256_file(source).casefold() != approved_sha:
        return _result(False, "stop_approved_file_changed", "presenter_file_hash_changed_after_approval")

    binding = item.get("remote_input_binding") or {}
    remote_id = str(binding.get("remote_avatar_id") or binding.get("remote_asset_id") or "").strip()
    if not remote_id:
        return _result(False, "bind_and_verify_exact_remote_avatar", "missing_remote_avatar_or_asset_id")
    if str(binding.get("sku") or "").strip() != sku:
        return _result(False, "stop_remote_binding_mismatch", "remote_binding_sku_mismatch")
    if str(binding.get("approved_sha256") or "").strip().casefold() != approved_sha:
        return _result(False, "stop_remote_binding_mismatch", "remote_binding_hash_mismatch")
    for field in (
        "remote_preview_verified",
        "preview_person_match",
        "preview_product_match",
        "preview_scene_match",
    ):
        if binding.get(field) is not True:
            return _result(False, "stop_remote_preview_mismatch", f"remote_preview_failed:{field}")

    return _result(True, "ready_to_submit_exact_remote_input")


def cross_sku_remote_binding_conflicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return remote avatar/asset IDs reused by more than one SKU."""

    by_remote_id: dict[str, set[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        binding = item.get("remote_input_binding") or {}
        remote_id = str(binding.get("remote_avatar_id") or binding.get("remote_asset_id") or "").strip()
        sku = str(item.get("sku") or "").strip()
        if remote_id and sku:
            by_remote_id.setdefault(remote_id, set()).add(sku)
    return [
        {"remote_id": remote_id, "skus": sorted(skus)}
        for remote_id, skus in sorted(by_remote_id.items())
        if len(skus) > 1
    ]


def evaluate_post_render(item: dict[str, Any]) -> dict[str, Any]:
    """Require the rendered sample to match the exact approved input at three points."""

    pre_submit = evaluate_pre_submit(item)
    if not pre_submit["approved"]:
        return pre_submit

    approval = item.get("presenter_approval") or {}
    approved_sha = str(approval.get("approved_sha256") or "").strip().casefold()
    qc = item.get("render_match_qc") or {}
    if qc.get("checked") is not True:
        return _result(False, "await_render_match_qc", "render_not_compared_to_approved_input")
    if str(qc.get("compared_to_approved_sha256") or "").strip().casefold() != approved_sha:
        return _result(False, "reject_remote_input_or_render_mismatch", "render_compared_to_wrong_approved_hash")

    frames = qc.get("frames") or {}
    checks = (
        "presenter_match",
        "exact_sku_product_match",
        "package_match",
        "scene_match",
        "placeholder_absent",
    )
    for point in FRAME_POINTS:
        frame = frames.get(point) or {}
        if not str(frame.get("path") or "").strip():
            return _result(False, "await_render_match_qc", f"missing_qc_frame:{point}")
        for check in checks:
            if frame.get(check) is not True:
                return _result(False, "reject_remote_input_or_render_mismatch", f"{point}_frame_failed:{check}")

    return _result(True, "completed_validated_against_exact_approved_input")


def audit_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in (manifest.get("items") or []) if isinstance(item, dict)]
    conflicts = cross_sku_remote_binding_conflicts(items)
    issues: list[dict[str, Any]] = []
    for item in items:
        status = str(item.get("status") or "").casefold()
        result = evaluate_post_render(item) if status.startswith("completed") else evaluate_pre_submit(item)
        if not result["approved"]:
            issues.append({"task_id": item.get("task_id"), "sku": item.get("sku"), **result})
    return {
        "passed": not conflicts and not issues,
        "cross_sku_remote_binding_conflicts": conflicts,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("pre-submit", "post-render", "audit-manifest"))
    parser.add_argument("json_path")
    args = parser.parse_args()
    payload = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    if args.mode == "pre-submit":
        result = evaluate_pre_submit(payload)
    elif args.mode == "post-render":
        result = evaluate_post_render(payload)
    else:
        result = audit_manifest(payload)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("approved", result.get("passed")) else 2


if __name__ == "__main__":
    raise SystemExit(main())
