#!/usr/bin/env python3
"""Conservative lexical near-copy check for a reference and a rewritten script."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def tokens(text: str) -> list[str]:
    return re.findall(r"[\w']+", text.casefold(), flags=re.UNICODE)


def ngrams(items: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(items[i:i + n]) for i in range(max(0, len(items) - n + 1))}


def sentences(text: str) -> list[list[str]]:
    return [tokens(value) for value in re.split(r"[.!?。！？\n]+", text) if tokens(value)]


def analyze(reference: str, rewrite: str) -> dict:
    ref_tokens = tokens(reference)
    out_tokens = tokens(rewrite)
    ref_8 = ngrams(ref_tokens, 8)
    out_8 = ngrams(out_tokens, 8)
    exact_8 = sorted(" ".join(value) for value in ref_8 & out_8)
    ref_sentences = sentences(reference)
    out_sentences = sentences(rewrite)
    max_jaccard = 0.0
    closest = None
    for ref in ref_sentences:
        for out in out_sentences:
            union = set(ref) | set(out)
            similarity = len(set(ref) & set(out)) / len(union) if union else 0.0
            if similarity > max_jaccard:
                max_jaccard = similarity
                closest = {"reference": " ".join(ref), "rewrite": " ".join(out)}
    ref_4 = ngrams(ref_tokens, 4)
    out_4 = ngrams(out_tokens, 4)
    fourgram_reuse = len(ref_4 & out_4) / max(1, len(out_4))
    high = bool(exact_8) or max_jaccard >= 0.58 or fourgram_reuse >= 0.35
    medium = not high and (max_jaccard >= 0.42 or fourgram_reuse >= 0.2)
    return {
        "similarity_risk": "high" if high else "medium" if medium else "low",
        "pass": not high,
        "exact_8_word_matches": exact_8,
        "max_sentence_jaccard": round(max_jaccard, 3),
        "fourgram_reuse_ratio": round(fourgram_reuse, 3),
        "closest_sentence_pair": closest,
        "thresholds": {
            "exact_consecutive_words": 8,
            "max_sentence_jaccard": 0.58,
            "fourgram_reuse_ratio": 0.35,
        },
        "note": "Lexical regression check only; human review is still required for unique expressions, identity, music, shots, and factual transfer.",
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("rewrite", type=Path)
    args = parser.parse_args()
    result = analyze(args.reference.read_text(encoding="utf-8"), args.rewrite.read_text(encoding="utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["pass"] else 2)


if __name__ == "__main__":
    main()
