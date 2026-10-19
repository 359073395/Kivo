from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_current_warehouse_source.py"
SPEC = importlib.util.spec_from_file_location("warehouse_source_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CurrentWarehouseSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault = Path(self.temp_dir.name) / "Knowledge"
        self.data_root = Path(self.temp_dir.name) / "TikTokSKU"
        self.pointer_dir = self.vault / "skill" / "tiktok-commerce-operations" / "references"
        self.pointer_dir.mkdir(parents=True)
        (self.vault / "辅助" / "配置").mkdir(parents=True)
        (self.vault / "资源" / "来源索引").mkdir(parents=True)
        (self.vault / "资产" / "报告").mkdir(parents=True)
        (self.data_root / "02_SKU定价源").mkdir(parents=True)
        (self.data_root / "04_输出结果").mkdir(parents=True)

        self.source = self.data_root / "02_SKU定价源" / "current.xlsx"
        self.source.write_bytes(b"current-source")
        self.source_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        (self.vault / "资源" / "来源索引" / "source.md").write_text("source", encoding="utf-8")
        (self.vault / "资产" / "报告" / "asset.md").write_text("asset", encoding="utf-8")
        (self.vault / "辅助" / "配置" / "machine-paths.local.json").write_text(
            json.dumps({"tiktokSkuRoot": str(self.data_root)}), encoding="utf-8"
        )
        self.pointer = {
            "configuredRoot": "tiktokSkuRoot",
            "sourceDate": "2026-09-12",
            "relativePath": "02_SKU定价源/current.xlsx",
            "sha256": self.source_sha,
            "sourceCard": "../../../资源/来源索引/source.md",
            "knowledgeAsset": "../../../资产/报告/asset.md",
            "derivedUnifiedPrices": {
                "relativePath": "04_输出结果/unified.xlsx",
                "status": "needs_rebuild_for_current_source",
            },
        }
        self.write_pointer()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_pointer(self) -> None:
        (self.pointer_dir / "current-warehouse-source.json").write_text(
            json.dumps(self.pointer), encoding="utf-8"
        )

    def test_source_read_verifies_current_hash(self) -> None:
        result, code = MODULE.validate(self.vault, "source-read")
        self.assertEqual(code, 0)
        self.assertTrue(result["allowed"])
        self.assertTrue(result["sourceHashVerified"])
        self.assertEqual(result["nextAction"], "read_current_source")

    def test_stale_derived_prices_block_flash_write(self) -> None:
        result, code = MODULE.validate(self.vault, "flash-write")
        self.assertEqual(code, 2)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["nextAction"], "stop_stale_unified_price_rebuild_required")

    def test_current_derived_prices_allow_flash_write(self) -> None:
        derived = self.data_root / "04_输出结果" / "unified.xlsx"
        derived.write_bytes(b"current-derived")
        self.pointer["derivedUnifiedPrices"].update(
            status="current_for_source",
            sourceSha256=self.source_sha,
            sha256=hashlib.sha256(derived.read_bytes()).hexdigest(),
        )
        self.write_pointer()
        result, code = MODULE.validate(self.vault, "flash-write")
        self.assertEqual(code, 0)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["nextAction"], "write_flash_from_current_unified_prices")

    def test_source_hash_mismatch_stops_all_use(self) -> None:
        self.pointer["sha256"] = "0" * 64
        self.write_pointer()
        result, code = MODULE.validate(self.vault, "source-read")
        self.assertEqual(code, 1)
        self.assertFalse(result["allowed"])
        self.assertIn("current source SHA-256 mismatch", result["errors"])

    def test_path_escape_is_rejected(self) -> None:
        self.pointer["relativePath"] = "../outside.xlsx"
        self.write_pointer()
        result, code = MODULE.validate(self.vault, "source-read")
        self.assertEqual(code, 1)
        self.assertFalse(result["allowed"])
        self.assertIn("relativePath is outside configured root", result["errors"])


if __name__ == "__main__":
    unittest.main()
