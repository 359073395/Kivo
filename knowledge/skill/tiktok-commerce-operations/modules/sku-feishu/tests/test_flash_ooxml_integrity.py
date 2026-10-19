import importlib.util
import os
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path

from lxml import etree


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"m": MAIN_NS}
SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "sync_weekly_flash_deals.py"
)


def build_template(path: Path) -> None:
    shared = etree.Element(f"{{{MAIN_NS}}}sst", nsmap={None: MAIN_NS})
    shared.set("count", "2")
    shared.set("uniqueCount", "2")
    for text in (
        "Product_id (required)",
        "Deal Price (required)",
    ):
        item = etree.SubElement(shared, f"{{{MAIN_NS}}}si")
        etree.SubElement(item, f"{{{MAIN_NS}}}t").text = text

    worksheet = etree.Element(f"{{{MAIN_NS}}}worksheet", nsmap={None: MAIN_NS})
    etree.SubElement(worksheet, f"{{{MAIN_NS}}}dimension", ref="A1:N12")
    sheet_data = etree.SubElement(worksheet, f"{{{MAIN_NS}}}sheetData")
    header = etree.SubElement(sheet_data, f"{{{MAIN_NS}}}row", r="1")
    for column, index in (("A", "0"), ("B", "1")):
        cell = etree.SubElement(
            header,
            f"{{{MAIN_NS}}}c",
            r=f"{column}1",
            t="s",
            s="1",
        )
        etree.SubElement(cell, f"{{{MAIN_NS}}}v").text = index
    for row_number in range(2, 13):
        row = etree.SubElement(sheet_data, f"{{{MAIN_NS}}}row", r=str(row_number))
        etree.SubElement(row, f"{{{MAIN_NS}}}c", r=f"A{row_number}", s="2")
        etree.SubElement(row, f"{{{MAIN_NS}}}c", r=f"B{row_number}", s="3")
        etree.SubElement(row, f"{{{MAIN_NS}}}c", r=f"E{row_number}", s="4")

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/sharedStrings.xml",
            etree.tostring(shared, xml_declaration=True, encoding="UTF-8"),
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            etree.tostring(worksheet, xml_declaration=True, encoding="UTF-8"),
        )


class FlashOoxmlIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        product_root = root / "products"
        product_root.mkdir()
        mapping = root / "mapping.json"
        mapping.write_text("[]", encoding="utf-8")
        unified_price = root / "unified.xlsx"
        unified_price.touch()
        os.environ.update(
            {
                "PRODUCT_ROOT": str(product_root),
                "STORE_MAPPING": str(mapping),
                "UNIFIED_PRICE_WORKBOOK": str(unified_price),
            }
        )
        sys.path.insert(0, str(SCRIPT_PATH.parent))
        spec = importlib.util.spec_from_file_location("sync_weekly_flash_deals", SCRIPT_PATH)
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_appended_rows_do_not_clone_populated_a_b_cells(self) -> None:
        workbook = Path(self.temp.name) / "Flash Deal.xlsx"
        build_template(workbook)
        rows = [
            {
                "product_id": str(1_730_000_000_000_000_000 + index),
                "offer_price": 35_000 + index,
            }
            for index in range(20)
        ]

        self.module.patch_flash(workbook, rows)

        with zipfile.ZipFile(workbook, "r") as archive:
            sheet = etree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        sheet_rows = {
            int(row.get("r")): row
            for row in sheet.findall(".//m:row", NS)
        }
        for row_number in range(2, 22):
            refs = [str(cell.get("r")) for cell in sheet_rows[row_number].findall("m:c", NS)]
            self.assertEqual(len(refs), len(set(refs)), f"row {row_number}: {refs}")
            self.assertEqual(refs.count(f"A{row_number}"), 1)
            self.assertEqual(refs.count(f"B{row_number}"), 1)

    def test_npcs_uses_unified_price_instead_of_blanket_exclusion(self) -> None:
        products = {
            "1730000000000000001": [
                {"sku": "2pcsKOPI SUScream", "listed_price": Decimal("100000")}
            ]
        }
        prices = {
            "2pcskopi suscream": {
                "selected_price": Decimal("87060"),
                "selected_source": "价格2",
                "status": "可用",
                "blocker": "",
            }
        }
        eligible, reasons = self.module.analyze_store(products, prices)
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]["offer_price"], 87060)
        self.assertEqual(reasons["npcs"], [])

    def test_npcs_can_be_temporarily_excluded_for_one_run(self) -> None:
        products = {
            "1730000000000000001": [
                {"sku": "2pcsKOPI SUScream", "listed_price": Decimal("100000")}
            ]
        }
        prices = {
            "2pcskopi suscream": {
                "selected_price": Decimal("87060"),
                "selected_source": "价格2",
                "status": "可用",
                "blocker": "",
            }
        }
        original = self.module.EXCLUDE_NPCS
        self.module.EXCLUDE_NPCS = True
        try:
            eligible, reasons = self.module.analyze_store(products, prices)
        finally:
            self.module.EXCLUDE_NPCS = original
        self.assertEqual(eligible, [])
        self.assertEqual(len(reasons["npcs"]), 1)

    def test_multi_sku_different_prices_is_blocked(self) -> None:
        products = {
            "1730000000000000002": [
                {"sku": "SKU-A", "listed_price": Decimal("100000")},
                {"sku": "SKU-B", "listed_price": Decimal("100000")},
            ]
        }
        prices = {
            "sku-a": {
                "selected_price": Decimal("45000"),
                "selected_source": "价格1",
                "status": "可用",
                "blocker": "",
            },
            "sku-b": {
                "selected_price": Decimal("47000"),
                "selected_source": "价格2",
                "status": "可用",
                "blocker": "",
            },
        }
        eligible, reasons = self.module.analyze_store(products, prices)
        self.assertEqual(eligible, [])
        self.assertEqual(len(reasons["multi_price"]), 1)


if __name__ == "__main__":
    unittest.main()
