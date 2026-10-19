#!/usr/bin/env python3
"""Run deterministic rewrite-fixture checks without web access."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from check_rewrite_similarity import analyze


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    fixture = json.loads((ROOT / "references/fixtures/rewrite-regression-fixture.json").read_text(encoding="utf-8"))
    reference = fixture["reference_transcript_id"]
    good = fixture["expected_safe_rewrite_id"]
    bad = fixture["known_bad_near_copy_id"]
    good_result = analyze(reference, good)
    bad_result = analyze(reference, bad)
    if not good_result["pass"] or bad_result["pass"]:
        raise SystemExit(json.dumps({"good": good_result, "bad": bad_result}, ensure_ascii=False, indent=2))
    forbidden = set(value.casefold() for value in fixture["forbidden_fact_transfer"])
    if any(value in good.casefold() for value in forbidden):
        raise SystemExit("Safe rewrite contains a forbidden reference-product fact")
    print("Rewrite fixture tests passed")
    print(json.dumps({"good": good_result, "bad": bad_result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
