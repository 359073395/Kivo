#!/usr/bin/env python3
"""Extract searchable Markdown from a DOCX using only Python's standard library."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def text_of(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return re.sub(r"[ \t]+", " ", "".join(parts)).strip()


def paragraph_markdown(paragraph: ET.Element) -> str:
    text = text_of(paragraph)
    if not text:
        return ""
    style = ""
    props = paragraph.find(W + "pPr")
    if props is not None:
        style_node = props.find(W + "pStyle")
        if style_node is not None:
            style = style_node.attrib.get(W + "val", "")
    match = re.search(r"(?:Heading|标题|heading)([1-6])", style, flags=re.I)
    if match:
        return f"{'#' * int(match.group(1))} {text}"
    if style.lower() in {"title", "标题"}:
        return f"# {text}"
    return text


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def table_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in table.findall(W + "tr"):
        cells = [escape_table_cell(text_of(cell)) for cell in row.findall(W + "tc")]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    header = rows[0]
    output = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * width) + " |"]
    output.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(output)


def extract_docx(source: Path) -> str:
    with zipfile.ZipFile(source) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(W + "body")
    if body is None:
        raise ValueError("DOCX has no document body")
    blocks: list[str] = []
    for child in body:
        if child.tag == W + "p":
            value = paragraph_markdown(child)
        elif child.tag == W + "tbl":
            value = table_markdown(child)
        else:
            value = ""
        if value:
            blocks.append(value)
    return "\n\n".join(blocks).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    extracted = extract_docx(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# TikTok 运营知识库（从 DOCX 提取）\n\n"
        f"原始文件：`{args.source.name}`\n\n"
        "> 本文件用于全文检索。原 DOCX 是内容来源；平台政策、功能和阈值可能变化，涉及当前规则时必须核对官方来源。\n\n"
    )
    args.output.write_text(header + extracted, encoding="utf-8")
    with zipfile.ZipFile(args.source) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        media_count = sum(name.startswith("word/media/") for name in archive.namelist())
    summary = {
        "source_file": args.source.name,
        "paragraph_count": len(root.findall(f".//{W}p")),
        "table_count": len(root.findall(f".//{W}tbl")),
        "embedded_media_count": media_count,
        "extracted_character_count": len(extracted),
        "extracted_markdown": args.output.name,
        "visual_render_status": "not_available_in_build_environment",
        "structural_validation": "word/document.xml parsed successfully",
    }
    summary_path = args.summary or args.output.with_name("operations_extraction_summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
