from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).parents[1] / "scripts" / "cleanup_rejected_media.py"
SPEC = importlib.util.spec_from_file_location("cleanup_rejected_media", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CleanupRejectedMediaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.presenter_dir = self.root / "SKU-A" / "06_人物与商品合成"
        self.presenter_dir.mkdir(parents=True)
        self.approved = self.presenter_dir / "SKU-A_用户最终批准图.png"
        self.approved.write_bytes(b"approved")
        self.rejected = self.presenter_dir / "SKU-A_v2_rejected.png"
        self.rejected.write_bytes(b"rejected")
        self.source = self.root / "SKU-A" / "01_产品资料" / "白底图" / "SKU-A.png"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b"source")
        self.intermediate = self.root / "SKU-A" / "01_产品资料" / "SKU-A_商品锁定透明层_v2.png"
        self.intermediate.write_bytes(b"intermediate")
        digest = hashlib.sha256(self.approved.read_bytes()).hexdigest()
        self.manifest = {
            "exact_presenter_reapproval": {
                "candidates": [
                    {"path": str(self.approved), "sha256": digest, "status": "user_approved_exact_file"}
                ]
            },
            "items": [],
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_cleanup_preserves_approved_and_source_images(self) -> None:
        files, dirs = MODULE.collect(self.root, self.manifest)
        MODULE.execute(self.root, files, dirs)
        self.assertTrue(self.approved.is_file())
        self.assertTrue(self.source.is_file())
        self.assertFalse(self.rejected.exists())
        self.assertFalse(self.intermediate.exists())

    def test_cleanup_removes_only_state_marked_invalid_remote_output(self) -> None:
        invalid = self.root / "SKU-A" / "07_HeyGen任务" / "bad.mp4"
        valid = self.root / "SKU-A" / "07_HeyGen任务" / "good.mp4"
        invalid.parent.mkdir(parents=True)
        invalid.write_bytes(b"bad")
        valid.write_bytes(b"good")
        self.manifest["items"] = [
            {"status": "invalidated", "output_path": str(invalid)},
            {"status": "completed_validated", "output_path": str(valid)},
        ]
        files, dirs = MODULE.collect(self.root, self.manifest)
        MODULE.execute(self.root, files, dirs)
        self.assertFalse(invalid.exists())
        self.assertTrue(valid.is_file())


if __name__ == "__main__":
    unittest.main()
