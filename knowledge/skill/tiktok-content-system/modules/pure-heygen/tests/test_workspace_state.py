from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).parents[1] / "scripts" / "workspace_state.py"
SPEC = importlib.util.spec_from_file_location("pure_heygen_workspace_state", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkflowDecisionTests(unittest.TestCase):
    def decide(self, **overrides: object) -> str:
        values = {
            "has_product": True,
            "has_approved_script_or_audio": True,
            "presenter_state": "approved",
            "sample_approved": True,
            "batch_approved": True,
            "batch_status": "in_progress",
        }
        values.update(overrides)
        return MODULE.decide_next_action(**values)

    def test_missing_product_stops(self) -> None:
        self.assertEqual(self.decide(has_product=False), "stop_missing_product")

    def test_missing_presenter_routes_upstream_without_choice(self) -> None:
        self.assertEqual(self.decide(presenter_state="missing"), "prepare_one_presenter_candidate")

    def test_missing_approved_audio_stops(self) -> None:
        self.assertEqual(
            self.decide(has_approved_script_or_audio=False),
            "stop_missing_approved_script_or_audio",
        )

    def test_unapproved_presenter_waits_at_actual_gate(self) -> None:
        self.assertEqual(self.decide(presenter_state="present_unapproved"), "await_presenter_approval")

    def test_approved_presenter_without_video_sample_generates_one(self) -> None:
        self.assertEqual(self.decide(sample_approved=False), "generate_one_video_sample")

    def test_approved_sample_continues_batch(self) -> None:
        self.assertEqual(self.decide(), "continue_serial_batch")

    def test_sample_approval_without_batch_instruction_waits(self) -> None:
        self.assertEqual(self.decide(batch_approved=False), "await_batch_approval")

    def test_newer_unapproved_test_does_not_replace_batch_standard(self) -> None:
        selected = MODULE.select_latest_batch_standard(
            [
                {
                    "standard_id": "v1",
                    "status": "active",
                    "batch_authorized": True,
                    "approved_at": "2026-08-27T15:06:34+07:00",
                },
                {
                    "standard_id": "v2",
                    "status": "candidate",
                    "batch_authorized": False,
                    "approved_at": "2026-08-29T16:20:00+07:00",
                },
            ]
        )
        self.assertEqual(selected["standard_id"], "v1")

    def test_latest_batch_approval_replaces_older_standard(self) -> None:
        selected = MODULE.select_latest_batch_standard(
            [
                {
                    "standard_id": "v1",
                    "status": "active",
                    "batch_authorized": True,
                    "approved_at": "2026-08-27T15:06:34+07:00",
                },
                {
                    "standard_id": "v2",
                    "status": "approved",
                    "batch_authorized": True,
                    "approved_at": "2026-08-29T16:20:00+07:00",
                },
            ]
        )
        self.assertEqual(selected["standard_id"], "v2")

    def test_explicit_user_render_review_overrides_older_agent_rejection(self) -> None:
        selected = MODULE.select_latest_batch_standard(
            [
                {
                    "standard_id": "STD-CNT-PURE-HEYGEN-20260908-01",
                    "status": "candidate",
                    "batch_authorized": False,
                    "approved_at": "2026-09-08T15:16:40+07:00",
                    "decision_source": "agent_visual_rejection",
                },
                {
                    "standard_id": "STD-CNT-PURE-HEYGEN-20260908-02",
                    "status": "active",
                    "batch_authorized": True,
                    "approved_at": "2026-09-08T15:39:50+07:00",
                    "decision_source": "explicit_user_render_review",
                    "normal_held_product_motion_accepted": True,
                    "wrong_sku_or_severe_deformation_still_blocking": True,
                },
            ]
        )
        self.assertEqual(selected["standard_id"], "STD-CNT-PURE-HEYGEN-20260908-02")
        self.assertTrue(selected["normal_held_product_motion_accepted"])
        self.assertTrue(selected["wrong_sku_or_severe_deformation_still_blocking"])

    def test_quota_block_wins_without_resubmission(self) -> None:
        self.assertEqual(
            self.decide(batch_status="paused_insufficient_heygen_credits"),
            "blocked_external_quota",
        )

    def test_unique_normalized_near_match_prevents_duplicate_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / "下周视频任务_5SKU_20260824-20260830"
            existing.mkdir()
            match, candidates = MODULE.unique_near_match(root / "下周视频任务 5SKU 20260824 20260830")
            self.assertEqual(match, existing)
            self.assertEqual(candidates, [existing])

    def test_completed_validated_batch_is_not_recovered_as_active(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            task_dir = Path(temporary)
            (task_dir / "ACTIVE_TASK.json").write_text(
                json.dumps(
                    {
                        "skill": "tiktok-content-system",
                        "mode": "pure_heygen",
                        "task_id": "finished-batch",
                        "batch_status": "completed_validated",
                    }
                ),
                encoding="utf-8",
            )
            self.assertIsNone(MODULE.manifest_candidate(task_dir, "test"))

    def test_completed_item_without_exact_remote_binding_is_not_trusted(self) -> None:
        item, result = MODULE.first_completed_binding_issue(
            {
                "items": [
                    {
                        "task_id": "sku-a-v01",
                        "sku": "SKU-A",
                        "status": "completed_validated",
                        "presenter_image": "missing.jpg",
                        "presenter_image_sha256": "not-an-approved-hash",
                    }
                ]
            }
        )
        self.assertEqual(item["task_id"], "sku-a-v01")
        self.assertEqual(result["action"], "await_presenter_approval")

    def test_invalidated_batch_stops_at_presenter_reapproval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            task_dir = Path(temporary)
            manifest = {
                "skill": "tiktok-content-system",
                "mode": "pure_heygen",
                "task_id": "fatal-mismatch",
                "batch_status": "invalidated_remote_input_mismatch",
                "items": [],
            }
            (task_dir / "ACTIVE_TASK.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            plan = MODULE.plan_task(task_dir)
            self.assertEqual(plan["next_action"], "await_presenter_reapproval")


if __name__ == "__main__":
    unittest.main()
