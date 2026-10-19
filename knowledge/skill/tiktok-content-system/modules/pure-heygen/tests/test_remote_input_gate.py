from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).parents[1] / "scripts" / "remote_input_gate.py"
SPEC = importlib.util.spec_from_file_location("remote_input_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RemoteInputBindingGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.image = Path(self.temporary.name) / "approved.jpg"
        self.image.write_bytes(b"exact-approved-presenter-image")
        self.sha = hashlib.sha256(self.image.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def item(self) -> dict:
        frame = {
            "path": "frame.jpg",
            "presenter_match": True,
            "exact_sku_product_match": True,
            "package_match": True,
            "scene_match": True,
            "placeholder_absent": True,
        }
        return {
            "task_id": "sku-a-v01",
            "sku": "SKU-A",
            "status": "pending",
            "presenter_image": str(self.image),
            "presenter_image_sha256": self.sha,
            "presenter_approval": {
                "status": "approved",
                "scope": "exact_sku_exact_file",
                "sku": "SKU-A",
                "approved_path": str(self.image),
                "approved_version": "v5",
                "approved_sha256": self.sha,
                "approved_at": "2026-09-06T20:00:00+07:00",
                "evidence": "direct user approval",
            },
            "remote_input_binding": {
                "remote_avatar_id": "avatar-a",
                "sku": "SKU-A",
                "approved_sha256": self.sha,
                "remote_preview_verified": True,
                "preview_person_match": True,
                "preview_product_match": True,
                "preview_scene_match": True,
            },
            "render_match_qc": {
                "checked": True,
                "compared_to_approved_sha256": self.sha,
                "frames": {"start": dict(frame), "middle": dict(frame), "end": dict(frame)},
            },
        }

    def test_exact_approval_and_remote_binding_can_submit(self) -> None:
        self.assertEqual(
            MODULE.evaluate_pre_submit(self.item())["action"],
            "ready_to_submit_exact_remote_input",
        )

    def test_one_sku_approval_cannot_authorize_another_sku(self) -> None:
        item = self.item()
        item["sku"] = "SKU-B"
        self.assertEqual(MODULE.evaluate_pre_submit(item)["action"], "stop_approval_sku_mismatch")

    def test_changed_or_derived_file_returns_to_approval(self) -> None:
        item = self.item()
        self.image.write_bytes(b"derived-after-user-approval")
        self.assertEqual(MODULE.evaluate_pre_submit(item)["action"], "stop_approved_file_changed")

    def test_contextual_multi_image_approval_must_name_the_displayed_asset_hash(self) -> None:
        item = self.item()
        item["presenter_approval"]["source_approval_type"] = "contextual_multi_image"
        item["presenter_approval"]["displayed_asset_sha256s"] = ["another-image-hash"]
        self.assertEqual(
            MODULE.evaluate_pre_submit(item)["action"],
            "stop_contextual_approval_asset_mismatch",
        )

        item["presenter_approval"]["displayed_asset_sha256s"] = [self.sha]
        self.assertEqual(
            MODULE.evaluate_pre_submit(item)["action"],
            "ready_to_submit_exact_remote_input",
        )

    def test_missing_remote_id_blocks_submission(self) -> None:
        item = self.item()
        item["remote_input_binding"].pop("remote_avatar_id")
        self.assertEqual(
            MODULE.evaluate_pre_submit(item)["action"],
            "bind_and_verify_exact_remote_avatar",
        )

    def test_wrong_remote_preview_blocks_submission(self) -> None:
        item = self.item()
        item["remote_input_binding"]["preview_product_match"] = False
        self.assertEqual(MODULE.evaluate_pre_submit(item)["action"], "stop_remote_preview_mismatch")

    def test_remote_avatar_cannot_be_reused_across_skus(self) -> None:
        first = self.item()
        second = self.item()
        second["sku"] = "SKU-B"
        second["remote_input_binding"]["sku"] = "SKU-B"
        conflicts = MODULE.cross_sku_remote_binding_conflicts([first, second])
        self.assertEqual(conflicts, [{"remote_id": "avatar-a", "skus": ["SKU-A", "SKU-B"]}])

    def test_render_must_be_compared_to_approved_image(self) -> None:
        item = self.item()
        item["render_match_qc"] = {"checked": False}
        self.assertEqual(MODULE.evaluate_post_render(item)["action"], "await_render_match_qc")

    def test_wrong_person_or_product_in_any_frame_rejects_render(self) -> None:
        item = self.item()
        item["render_match_qc"]["frames"]["middle"]["exact_sku_product_match"] = False
        self.assertEqual(
            MODULE.evaluate_post_render(item)["action"],
            "reject_remote_input_or_render_mismatch",
        )

    def test_three_matching_frames_can_complete(self) -> None:
        self.assertEqual(
            MODULE.evaluate_post_render(self.item())["action"],
            "completed_validated_against_exact_approved_input",
        )


if __name__ == "__main__":
    unittest.main()
