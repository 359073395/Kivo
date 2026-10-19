#!/usr/bin/env python3
"""Local, evidence-based TikTok creator screening from authorized CSV/XLSX exports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import posixpath
import random
import re
import statistics
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


VERSION = "v3.0-free-export"
UNKNOWN_VALUES = {
    "", "unknown", "n/a", "na", "none", "null", "-", "—", "待补充", "未知", "nan",
}
TRUE_VALUES = {"true", "1", "yes", "y", "是"}
FALSE_VALUES = {"false", "0", "no", "n", "否"}

SCORE_GROUPS: dict[str, list[tuple[str, int]]] = {
    "audience_match_score": [
        ("audience_country_language_score", 8),
        ("audience_core_profile_score", 8),
        ("audience_interest_category_score", 8),
        ("audience_use_case_score", 6),
    ],
    "content_ability_score": [
        ("content_hook_score", 5),
        ("content_demo_score", 5),
        ("content_expression_score", 5),
        ("content_production_score", 5),
        ("content_stability_score", 5),
    ],
    "commerce_efficiency_score": [
        ("commerce_view_fit_score", 6),
        ("commerce_purchase_intent_score", 5),
        ("commerce_content_ratio_score", 4),
        ("commerce_explanation_cta_score", 5),
        ("commerce_data_score", 5),
    ],
    "cooperation_score": [
        ("cooperation_contact_score", 5),
        ("cooperation_budget_score", 5),
        ("cooperation_history_score", 5),
        ("cooperation_schedule_logistics_score", 5),
    ],
}
SCORE_FIELDS = [item for group in SCORE_GROUPS.values() for item in group]
TOTAL_EVIDENCE_COMPONENTS = len(SCORE_FIELDS) + 1  # includes risk_deduction

RAW_EXPORT_FIELDS = [
    "creator_handle", "creator_url", "nickname", "country", "language", "followers",
    "recent_views", "engagement_rate_pct", "content_category", "audience_profile",
    "commerce_metrics", "authorized_gmv", "units_sold", "avg_shoppable_video_views",
    "video_engagement_rate_pct", "audience_female_pct", "audience_top_age_range",
    "category_gmv_distribution", "contact_channel", "sample_contact_status", "notes",
    "creator_type", "recent_content_observation", "personalization_verified",
    "content_category_relevance", "days_since_last_post", "risk_level", "do_not_contact",
    "commission_pct", "estimated_cash_fee",
]
MANUAL_SCORE_FIELDS = [field for field, _maximum in SCORE_FIELDS] + ["risk_deduction"]
REVIEW_EVIDENCE_FIELDS = [
    "reviewed_video_count", "reviewed_video_urls", "hook_evidence", "demo_evidence",
    "expression_evidence", "production_evidence", "stability_evidence",
    "purchase_intent_comment_evidence", "commerce_content_ratio_evidence",
    "commerce_explanation_cta_evidence", "risk_review_evidence",
]
TRACEABILITY_FIELDS = [
    "data_facts", "content_inference", "manual_verification", "evidence_sources",
    "risk_points", "recommended_strategy_override",
]
CANONICAL_INPUT_FIELDS = RAW_EXPORT_FIELDS + MANUAL_SCORE_FIELDS + REVIEW_EVIDENCE_FIELDS + TRACEABILITY_FIELDS

CORE_PROFILE_FIELDS = ["country", "language", "followers", "content_category"]
QUALITY_FIELDS = [
    "creator_handle", "creator_url", "country", "language", "followers", "recent_views",
    "engagement_rate_pct", "content_category", "audience_profile", "commerce_metrics",
    "contact_channel",
]

HEADER_ALIASES: dict[str, list[str]] = {
    "creator_handle": [
        "handle", "username", "creator username", "creator_username", "tiktok username",
        "tiktok_username", "creator handle", "creator unique id", "达人账号", "达人用户名",
        "用户名", "tiktok账号", "达人id", "creator id",
    ],
    "creator_url": [
        "profile url", "profile_url", "profile link", "creator link", "tiktok link",
        "主页链接", "达人主页", "达人链接", "账号链接", "主页",
    ],
    "nickname": ["creator name", "display name", "name", "达人昵称", "昵称", "creator nickname"],
    "country": ["creator country", "country/region", "country region", "market", "region", "国家", "国家/地区", "达人国家", "市场"],
    "language": ["content language", "creator language", "main language", "语言", "内容语言", "主要语言"],
    "followers": ["follower count", "followers count", "follower_count", "fans", "粉丝数", "粉丝量", "粉丝"],
    "recent_views": [
        "recent video views", "recent views", "video views", "average video views", "avg video views",
        "近期播放量", "近期视频播放", "最近视频播放", "平均播放量",
    ],
    "engagement_rate_pct": ["engagement rate", "engagement_rate", "互动率", "平均互动率"],
    "content_category": ["category", "creator category", "primary category", "content niche", "niche", "内容类目", "达人类目", "主营类目", "类目"],
    "audience_profile": ["audience", "audience profile", "audience demographics", "受众画像", "粉丝画像", "受众"],
    "commerce_metrics": ["commerce data", "sales metrics", "带货数据", "电商数据", "成交数据"],
    "authorized_gmv": ["gmv", "30d gmv", "gmv 30d", "近30天gmv", "30天gmv", "成交金额"],
    "units_sold": ["units sold", "sales volume", "items sold", "30d units sold", "销量", "销售件数", "成交件数"],
    "avg_shoppable_video_views": [
        "average shoppable video views", "avg shoppable video views", "avg ec video plays",
        "平均带货视频播放", "带货视频平均播放量", "平均电商视频播放",
    ],
    "video_engagement_rate_pct": ["video engagement rate", "ec video engagement rate", "带货视频互动率", "视频互动率"],
    "audience_female_pct": ["female audience", "female audience pct", "female followers", "女性粉丝占比", "女性受众占比"],
    "audience_top_age_range": ["top age range", "audience age", "main age range", "主要年龄段", "粉丝年龄段"],
    "category_gmv_distribution": ["category gmv distribution", "top category", "主营类目gmv", "类目gmv分布", "成交类目分布"],
    "contact_channel": ["contact", "contact info", "email", "contact method", "联系方式", "联系渠道", "邮箱"],
    "sample_contact_status": ["contact status", "outreach status", "建联状态", "联系状态"],
    "notes": ["remark", "remarks", "comment", "备注", "说明"],
    "creator_type": ["creator type", "达人类型"],
    "recent_content_observation": ["content observation", "recent content observation", "近期内容观察", "个性化观察"],
    "personalization_verified": ["personalization verified", "内容观察已核验", "个性化已核验"],
    "content_category_relevance": ["category relevance", "content relevance", "类目相关性", "内容相关性"],
    "days_since_last_post": ["days since last post", "inactive days", "距上次发布天数", "停更天数"],
    "risk_level": ["risk level", "风险等级"],
    "do_not_contact": ["do not contact", "dnc", "勿扰", "禁止联系"],
    "commission_pct": ["commission", "commission rate", "佣金", "佣金率"],
    "estimated_cash_fee": ["cash fee", "estimated fee", "creator fee", "报价", "预估报价", "现金费用"],
}

RANKED_FIELDS = [
    "rank", "row_number", "source_sheet", "creator_handle", "creator_url", "nickname", "country",
    "language", "followers", "recent_views_median", "engagement_rate_pct", "content_category",
    "authorized_gmv", "units_sold", "avg_shoppable_video_views", "video_engagement_rate_pct",
    "audience_female_pct", "audience_top_age_range", "category_gmv_distribution", "grade",
    "score_status", "total_score", "positive_score", "known_positive_score", "possible_score_range",
    "evidence_coverage_pct", "risk_deduction", "audience_match_score", "content_ability_score",
    "commerce_efficiency_score", "cooperation_score", "reviewed_video_count", "data_facts",
    "content_inference", "manual_verification", "evidence_sources", "missing_data", "risk_points",
    "recommended_strategy", "recommendation", "next_action", "manual_calibration_sample",
    "review_status", "model_version",
]
DRAFT_FIELDS = [
    "creator_handle", "nickname", "grade", "total_score", "recommended_strategy",
    "strategy_reason", "tiktok_dm", "email_subject", "email_body", "follow_up_48_72h",
    "sample_communication", "draft_readiness", "personalization_needs_verification",
    "review_status", "send_status", "contact_status", "message_version",
]
QUEUE_PREFIX_FIELDS = [
    "queue_priority", "selection_stage", "selection_reason", "current_grade", "current_total_score",
    "evidence_coverage_pct", "missing_data", "recommended_video_review_count", "deep_review_status",
    "source_row_number", "source_sheet",
]
NORMALIZED_FIELDS = ["source_row_number", "source_sheet"] + CANONICAL_INPUT_FIELDS


@dataclass
class Issue:
    row_number: int
    creator_handle: str
    severity: str
    field: str
    issue_type: str
    message: str
    manual_action: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def text_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def is_unknown(value: Any) -> bool:
    return text_value(value).lower() in UNKNOWN_VALUES


def display_or_unknown(value: Any) -> str:
    return "unknown" if is_unknown(value) else text_value(value)


def normalize_handle(value: Any) -> str:
    handle = text_value(value).lower().strip()
    return handle[1:] if handle.startswith("@") else handle


def normalize_url(value: Any) -> str:
    return text_value(value).lower().rstrip("/")


def normalize_header(value: Any) -> str:
    raw = text_value(value).replace("\ufeff", "").lower()
    return re.sub(r"[\s_\-–—/\\()（）%％:：]+", "", raw)


def parse_float(value: Any) -> float | None:
    if is_unknown(value):
        return None
    raw = text_value(value).replace(",", "").replace("%", "").replace("％", "").strip()
    raw = re.sub(r"^[A-Za-z]{3}\s*", "", raw)
    raw = raw.lstrip("$€£¥Rp ")
    multiplier = 1.0
    if raw and raw[-1].lower() in {"k", "m", "b"}:
        multiplier = {"k": 1_000.0, "m": 1_000_000.0, "b": 1_000_000_000.0}[raw[-1].lower()]
        raw = raw[:-1]
    try:
        number = float(raw) * multiplier
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def parse_int(value: Any) -> int | None:
    number = parse_float(value)
    if number is None or number < 0:
        return None
    return int(round(number))


def parse_bool(value: Any) -> bool | None:
    raw = text_value(value).lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return None


def canonical_language(value: Any) -> str:
    raw = text_value(value).lower().replace("_", "-")
    aliases = {
        "english": "en", "en-us": "en", "en-gb": "en", "英语": "en",
        "bahasa indonesia": "id", "indonesian": "id", "id-id": "id", "印尼语": "id",
        "chinese": "zh", "zh-cn": "zh", "mandarin": "zh", "中文": "zh",
    }
    return aliases.get(raw, raw)


def split_views(value: Any) -> tuple[list[int], list[str]]:
    if is_unknown(value):
        return [], []
    values: list[int] = []
    warnings: list[str] = []
    for part in re.split(r"[|;/；、]", text_value(value)):
        number = parse_int(part)
        if number is None:
            warnings.append(part.strip())
        else:
            values.append(number)
    return values, warnings


def score_label(total: float) -> str:
    if total >= 80:
        return "A"
    if total >= 65:
        return "B"
    if total >= 50:
        return "C"
    return "D"


def fmt_number(number: float | int | None) -> str:
    if number is None:
        return "unknown"
    if float(number).is_integer():
        return str(int(number))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def add_issue(
    issues: list[Issue], row_number: int, handle: str, severity: str, field: str,
    issue_type: str, message: str, action: str,
) -> None:
    issues.append(Issue(row_number, handle, severity, field, issue_type, message, action))


def build_alias_index(custom_mapping: dict[str, str] | None = None) -> dict[str, str]:
    index: dict[str, str] = {}
    for target in CANONICAL_INPUT_FIELDS:
        index[normalize_header(target)] = target
    for target, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            index[normalize_header(alias)] = target
    if custom_mapping:
        index.update(custom_mapping)
    return index


def load_custom_mapping(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Header mapping must be a JSON object")
    mapping: dict[str, str] = {}
    canonical = set(CANONICAL_INPUT_FIELDS)
    for key, value in data.items():
        if key in canonical:
            sources = value if isinstance(value, list) else [value]
            for source in sources:
                if not isinstance(source, str):
                    raise ValueError(f"Invalid source header for {key}")
                mapping[normalize_header(source)] = key
        elif isinstance(value, str) and value in canonical:
            mapping[normalize_header(key)] = value
        else:
            raise ValueError(f"Invalid mapping entry: {key} -> {value}")
    return mapping


def read_delimited_matrix(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8-sig")
    sample = text[:8192]
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",\t;").delimiter
    except csv.Error:
        pass
    return [[text_value(value) for value in row] for row in csv.reader(text.splitlines(), delimiter=delimiter)]


def excel_column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Za-z]+)", cell_ref)
    if not match:
        return 0
    index = 0
    for char in match.group(1).upper():
        index = index * 26 + ord(char) - 64
    return index - 1


def read_xlsx_matrices(path: Path) -> list[tuple[str, list[list[str]]]]:
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{{{main_ns}}}si"):
                shared.append("".join(node.text or "" for node in item.iter(f"{{{main_ns}}}t")))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{{{pkg_rel_ns}}}Relationship")
        }
        result: list[tuple[str, list[list[str]]]] = []
        sheets = workbook.find(f"{{{main_ns}}}sheets")
        if sheets is None:
            return result
        for sheet in sheets.findall(f"{{{main_ns}}}sheet"):
            name = sheet.attrib.get("name", "Sheet")
            rel_id = sheet.attrib.get(f"{{{rel_ns}}}id")
            if not rel_id or rel_id not in targets:
                continue
            target = targets[rel_id].lstrip("/")
            sheet_path = target if target.startswith("xl/") else posixpath.normpath(posixpath.join("xl", target))
            if sheet_path not in archive.namelist():
                continue
            root = ET.fromstring(archive.read(sheet_path))
            matrix: list[list[str]] = []
            sheet_data = root.find(f"{{{main_ns}}}sheetData")
            if sheet_data is None:
                result.append((name, matrix))
                continue
            for row_node in sheet_data.findall(f"{{{main_ns}}}row"):
                row_index = int(row_node.attrib.get("r", len(matrix) + 1)) - 1
                while len(matrix) <= row_index:
                    matrix.append([])
                row = matrix[row_index]
                for cell in row_node.findall(f"{{{main_ns}}}c"):
                    column = excel_column_index(cell.attrib.get("r", "A1"))
                    while len(row) <= column:
                        row.append("")
                    cell_type = cell.attrib.get("t", "")
                    value_node = cell.find(f"{{{main_ns}}}v")
                    if cell_type == "inlineStr":
                        inline = cell.find(f"{{{main_ns}}}is")
                        value = "" if inline is None else "".join(node.text or "" for node in inline.iter(f"{{{main_ns}}}t"))
                    elif value_node is None:
                        value = ""
                    elif cell_type == "s":
                        try:
                            value = shared[int(value_node.text or "0")]
                        except (ValueError, IndexError):
                            value = ""
                    elif cell_type == "b":
                        value = "true" if value_node.text == "1" else "false"
                    else:
                        value = value_node.text or ""
                    row[column] = text_value(value)
            result.append((name, matrix))
        return result


def header_match_score(row: list[str], aliases: dict[str, str]) -> tuple[int, int]:
    targets = {aliases.get(normalize_header(value)) for value in row if normalize_header(value) in aliases}
    targets.discard(None)
    identity = int("creator_handle" in targets or "creator_url" in targets)
    core = len(set(CORE_PROFILE_FIELDS) & targets)
    return identity * 100 + core * 10 + len(targets), len(targets)


def detect_header(matrix: list[list[str]], aliases: dict[str, str], explicit_row: int | None) -> tuple[int, int, int]:
    if explicit_row is not None:
        index = explicit_row - 1
        if index < 0 or index >= len(matrix):
            raise ValueError(f"Header row {explicit_row} is outside the sheet")
        score, count = header_match_score(matrix[index], aliases)
        return index, score, count
    best = (-1, -1, -1)
    for index, row in enumerate(matrix[:30]):
        score, count = header_match_score(row, aliases)
        candidate = (score, count, -index)
        if candidate > (best[1], best[2], -best[0]):
            best = (index, score, count)
    if best[0] < 0 or best[2] == 0:
        raise ValueError("Could not detect a mapped header row; provide --header-row or --mapping")
    return best


def canonicalize_matrix(
    matrix: list[list[str]], sheet_name: str, input_path: Path, aliases: dict[str, str],
    header_index: int,
) -> tuple[list[str], list[dict[str, str]], dict[str, Any]]:
    source_headers = [text_value(value) for value in matrix[header_index]]
    mapped_columns: list[tuple[int, str, str]] = []
    unmapped: list[str] = []
    targets_seen: Counter[str] = Counter()
    for index, source in enumerate(source_headers):
        if is_unknown(source):
            continue
        target = aliases.get(normalize_header(source))
        if target:
            mapped_columns.append((index, source, target))
            targets_seen[target] += 1
        else:
            unmapped.append(source)
    headers = list(dict.fromkeys(target for _index, _source, target in mapped_columns))
    rows: list[dict[str, str]] = []
    for source_index, values in enumerate(matrix[header_index + 1 :], start=header_index + 2):
        if not any(not is_unknown(value) for value in values):
            continue
        row = {field: "" for field in headers}
        for column, _source, target in mapped_columns:
            value = values[column] if column < len(values) else ""
            if is_unknown(row.get(target)) and not is_unknown(value):
                row[target] = text_value(value)
        row["_source_row_number"] = str(source_index)
        row["_source_sheet"] = sheet_name
        row["_input_file"] = str(input_path.resolve())
        rows.append(row)
    metadata = {
        "selected_sheet": sheet_name,
        "header_row": header_index + 1,
        "source_columns": [header for header in source_headers if not is_unknown(header)],
        "mapped_columns": [{"source": source, "target": target} for _index, source, target in mapped_columns],
        "unmapped_source_columns": unmapped,
        "duplicate_target_columns": [target for target, count in targets_seen.items() if count > 1],
        "mapped_target_columns": headers,
    }
    return headers, rows, metadata


def read_table(
    path: Path, sheet_name: str | None = None, header_row: int | None = None,
    mapping_path: Path | None = None,
) -> tuple[list[str], list[dict[str, str]], dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")
    custom_mapping = load_custom_mapping(mapping_path)
    aliases = build_alias_index(custom_mapping)
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        matrices = [(path.stem, read_delimited_matrix(path))]
        input_format = suffix.lstrip(".")
    elif suffix == ".xlsx":
        matrices = read_xlsx_matrices(path)
        input_format = "xlsx"
    elif suffix == ".xls":
        raise ValueError("Legacy .xls is not supported; export it as .xlsx or .csv")
    else:
        raise ValueError("Input must be .csv, .tsv, or .xlsx")
    if not matrices:
        raise ValueError("Input workbook has no readable worksheets")

    candidates: list[tuple[int, int, int, str, list[list[str]]]] = []
    for name, matrix in matrices:
        if sheet_name and name.casefold() != sheet_name.casefold():
            continue
        try:
            index, score, count = detect_header(matrix, aliases, header_row)
        except ValueError:
            if sheet_name:
                raise
            continue
        candidates.append((score, count, len(matrix) - index - 1, name, matrix))
    if not candidates:
        available = ", ".join(name for name, _matrix in matrices)
        raise ValueError(f"No suitable data sheet found. Available sheets: {available}")
    _score, _count, _rows, selected_name, selected_matrix = max(candidates, key=lambda item: item[:3])
    selected_header, _score, _count = detect_header(selected_matrix, aliases, header_row)
    headers, rows, metadata = canonicalize_matrix(selected_matrix, selected_name, path, aliases, selected_header)
    metadata.update({
        "input_file": str(path.resolve()),
        "input_format": input_format,
        "custom_mapping_file": str(mapping_path.resolve()) if mapping_path else None,
        "api_calls": 0,
        "paid_data_sources": "none",
    })
    if not ({"creator_handle", "creator_url"} & set(headers)):
        raise ValueError("Mapped input needs creator_handle or creator_url; use --mapping for the export's identity column")
    return headers, rows, metadata


def derive_handle_from_url(value: Any) -> str:
    match = re.search(r"tiktok\.com/@([^/?#]+)", text_value(value), flags=re.IGNORECASE)
    return f"@{match.group(1)}" if match else ""


def prepare_row(row: dict[str, str]) -> tuple[dict[str, str], bool]:
    result = {field: text_value(row.get(field)) for field in CANONICAL_INPUT_FIELDS}
    derived = False
    if is_unknown(result.get("creator_handle")) and not is_unknown(result.get("creator_url")):
        handle = derive_handle_from_url(result["creator_url"])
        if handle:
            result["creator_handle"] = handle
            derived = True
    for key in ["_source_row_number", "_source_sheet", "_input_file"]:
        result[key] = text_value(row.get(key))
    return result, derived


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Campaign config must be a JSON object")
    return data


def strategy_for(row: dict[str, str]) -> tuple[str, str]:
    override = text_value(row.get("recommended_strategy_override"))
    if not is_unknown(override):
        return override, "人工已明确覆盖默认策略；发送前仍需复核商务条件。"
    mapping = {
        "emerging_potential": ("样品 + 纯佣", "成长型达人适合从低风险小规模测试开始。"),
        "stable_publisher": ("样品 + 阶梯佣金", "稳定发布者可用阶梯机制鼓励持续产出。"),
        "high_quality_content": ("付费 + 佣金", "高质量内容型达人通常需要同时评估制作费和转化激励。"),
        "live": ("佣金 + 直播专属折扣", "直播型达人需要确认排期、库存和直播间优惠。"),
        "high_volume": ("定制商务方案", "大体量达人应单独确认报价、授权与交付范围。"),
    }
    return mapping.get(text_value(row.get("creator_type")).lower(), (
        "小规模测试，商务条件待确认", "达人类型或商务数据不足，先人工确认合作方式。",
    ))


def hard_filter_reasons(row: dict[str, str], config: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    target_market = text_value(config.get("market")).upper()
    target_languages = {canonical_language(value) for value in config.get("languages", [])}
    country = text_value(row.get("country")).upper()
    language = canonical_language(row.get("language"))
    hard = config.get("hard_filters", {}) if isinstance(config.get("hard_filters"), dict) else {}

    if is_unknown(row.get("creator_handle")):
        reasons.append("missing_identity:creator_handle_or_parseable_creator_url")
    if target_market and country and country != "UNKNOWN" and country != target_market:
        reasons.append(f"market_mismatch:{country}!={target_market}")
    if target_languages and language and language != "unknown" and language not in target_languages:
        reasons.append(f"language_mismatch:{language}")
    if text_value(row.get("content_category_relevance")).lower() == "unrelated":
        reasons.append("content_category_unrelated")

    followers = parse_int(row.get("followers"))
    minimum = parse_int(hard.get("min_followers"))
    maximum = parse_int(hard.get("max_followers"))
    if followers is not None and minimum is not None and followers < minimum:
        reasons.append(f"followers_below_min:{followers}<{minimum}")
    if followers is not None and maximum is not None and followers > maximum:
        reasons.append(f"followers_above_max:{followers}>{maximum}")
    inactive = parse_int(row.get("days_since_last_post"))
    max_inactive = parse_int(hard.get("max_days_since_last_post"))
    if inactive is not None and max_inactive is not None and inactive > max_inactive:
        reasons.append(f"inactive:{inactive}>{max_inactive}_days")
    if hard.get("exclude_high_risk", True) and text_value(row.get("risk_level")).lower() == "high":
        reasons.append("high_brand_safety_risk")
    if parse_bool(row.get("do_not_contact")) is True:
        reasons.append("do_not_contact")
    if hard.get("require_contact", False) and is_unknown(row.get("contact_channel")):
        reasons.append("missing_contact_channel")

    commission = parse_float(row.get("commission_pct"))
    max_commission = parse_float(hard.get("max_commission_pct"))
    if hard.get("commission_is_hard_limit", False) and commission is not None and max_commission is not None and commission > max_commission:
        reasons.append(f"commission_over_budget:{fmt_number(commission)}>{fmt_number(max_commission)}")
    cash_fee = parse_float(row.get("estimated_cash_fee"))
    max_cash = parse_float(hard.get("max_cash_fee"))
    if hard.get("cash_fee_is_hard_limit", False) and cash_fee is not None and max_cash is not None and cash_fee > max_cash:
        reasons.append(f"cash_fee_over_budget:{fmt_number(cash_fee)}>{fmt_number(max_cash)}")
    return reasons


def validate_row(row: dict[str, str], row_number: int, issues: list[Issue], handle_was_derived: bool = False) -> None:
    handle = display_or_unknown(row.get("creator_handle"))
    if is_unknown(row.get("creator_handle")):
        add_issue(issues, row_number, handle, "error", "creator_handle", "missing_identity", "达人账号缺失且无法从主页链接推导。", "补充达人账号或标准 TikTok 主页链接。")
    elif handle_was_derived:
        add_issue(issues, row_number, handle, "info", "creator_handle", "derived_from_url", "达人账号已从主页链接安全提取。", "人工抽查链接与账号是否一致。")
    for field in CORE_PROFILE_FIELDS:
        if is_unknown(row.get(field)):
            add_issue(issues, row_number, handle, "warning", field, "missing_core_profile", f"核心字段 {field} 为 unknown。", "可继续进入待补数队列；获得授权数据后再补充。")
    for field in QUALITY_FIELDS:
        if field not in CORE_PROFILE_FIELDS and field != "creator_handle" and is_unknown(row.get(field)):
            add_issue(issues, row_number, handle, "warning", field, "missing_recommended", f"建议字段 {field} 为 unknown。", "如可从后台导出则补充；不得用 0 代替未知。")
    for field in ["followers", "days_since_last_post", "reviewed_video_count", "units_sold"]:
        if not is_unknown(row.get(field)) and parse_int(row.get(field)) is None:
            add_issue(issues, row_number, handle, "error", field, "invalid_number", f"{field} 不是有效非负数字。", "统一为不带说明文字的数字；K/M 缩写可以保留。")
    for field in ["engagement_rate_pct", "video_engagement_rate_pct", "audience_female_pct", "commission_pct"]:
        if not is_unknown(row.get(field)) and parse_float(row.get(field)) is None:
            add_issue(issues, row_number, handle, "warning", field, "invalid_percentage", f"{field} 格式无法解析。", "使用百分数数值，例如 4.2 表示 4.2%。")
    _, bad_views = split_views(row.get("recent_views"))
    if bad_views:
        add_issue(issues, row_number, handle, "warning", "recent_views", "invalid_view_value", f"无法解析播放量：{'|'.join(bad_views)}。", "使用 | 分隔非负数字，支持 K/M 缩写。")
    for field, maximum in SCORE_FIELDS + [("risk_deduction", 20)]:
        if is_unknown(row.get(field)):
            continue
        value = parse_float(row.get(field))
        if value is None or value < 0 or value > maximum:
            add_issue(issues, row_number, handle, "error", field, "score_out_of_range", f"{field} 必须在 0–{maximum} 之间或为 unknown。", "根据证据重新评分，缺少证据时留空。")

    evidence_by_score = {
        "content_hook_score": "hook_evidence", "content_demo_score": "demo_evidence",
        "content_expression_score": "expression_evidence", "content_production_score": "production_evidence",
        "content_stability_score": "stability_evidence",
        "commerce_purchase_intent_score": "purchase_intent_comment_evidence",
        "commerce_content_ratio_score": "commerce_content_ratio_evidence",
        "commerce_explanation_cta_score": "commerce_explanation_cta_evidence",
        "risk_deduction": "risk_review_evidence",
    }
    for score_field, evidence_field in evidence_by_score.items():
        if not is_unknown(row.get(score_field)) and is_unknown(row.get(evidence_field)):
            add_issue(issues, row_number, handle, "warning", evidence_field, "score_without_evidence", f"{score_field} 已填写，但没有对应证据。", "补充视频链接、评论样本或人工观察依据。")
    reviewed_count = parse_int(row.get("reviewed_video_count"))
    if reviewed_count is not None and reviewed_count < 10 and any(not is_unknown(row.get(field)) for field in ["content_hook_score", "content_demo_score", "content_stability_score"]):
        add_issue(issues, row_number, handle, "warning", "reviewed_video_count", "content_sample_too_small", "内容评分样本少于 10 条视频。", "优先补足最近 10–20 条再确认内容稳定性。")


def combine_text(parts: Iterable[Any]) -> str:
    seen: set[str] = set()
    result: list[str] = []
    for part in parts:
        value = text_value(part)
        if is_unknown(value) or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return "；".join(result) if result else "unknown"


def structured_facts(row: dict[str, str], views_median: float | None) -> str:
    facts: list[str] = []
    if not is_unknown(row.get("country")) or not is_unknown(row.get("language")):
        facts.append(f"市场/语言={display_or_unknown(row.get('country'))}/{display_or_unknown(row.get('language'))}")
    pairs = [
        ("粉丝", row.get("followers")), ("近期播放中位数", fmt_number(views_median)),
        ("互动率%", row.get("engagement_rate_pct")), ("授权GMV", row.get("authorized_gmv")),
        ("销量", row.get("units_sold")), ("平均带货视频播放", row.get("avg_shoppable_video_views")),
        ("带货视频互动率%", row.get("video_engagement_rate_pct")),
        ("女性受众%", row.get("audience_female_pct")), ("主要年龄段", row.get("audience_top_age_range")),
        ("类目GMV分布", row.get("category_gmv_distribution")),
    ]
    for label, value in pairs:
        if not is_unknown(value):
            facts.append(f"{label}={text_value(value)}")
    return combine_text(facts)


def score_row(row: dict[str, str], row_number: int, scoring_model_approved: bool) -> dict[str, Any]:
    views, _bad = split_views(row.get("recent_views"))
    views_median = statistics.median(views) if views else None
    input_reference = f"{Path(row.get('_input_file', '')).name}#{row.get('_source_sheet', 'sheet')}!row{row_number}"
    result: dict[str, Any] = {
        "row_number": row_number,
        "source_sheet": display_or_unknown(row.get("_source_sheet")),
        "creator_handle": display_or_unknown(row.get("creator_handle")),
        "creator_url": display_or_unknown(row.get("creator_url")),
        "nickname": display_or_unknown(row.get("nickname")),
        "country": display_or_unknown(row.get("country")),
        "language": display_or_unknown(row.get("language")),
        "followers": display_or_unknown(row.get("followers")),
        "recent_views_median": fmt_number(views_median),
        "engagement_rate_pct": display_or_unknown(row.get("engagement_rate_pct")),
        "content_category": display_or_unknown(row.get("content_category")),
        "authorized_gmv": display_or_unknown(row.get("authorized_gmv")),
        "units_sold": display_or_unknown(row.get("units_sold")),
        "avg_shoppable_video_views": display_or_unknown(row.get("avg_shoppable_video_views")),
        "video_engagement_rate_pct": display_or_unknown(row.get("video_engagement_rate_pct")),
        "audience_female_pct": display_or_unknown(row.get("audience_female_pct")),
        "audience_top_age_range": display_or_unknown(row.get("audience_top_age_range")),
        "category_gmv_distribution": display_or_unknown(row.get("category_gmv_distribution")),
        "reviewed_video_count": display_or_unknown(row.get("reviewed_video_count")),
        "data_facts": combine_text([row.get("data_facts"), structured_facts(row, views_median)]),
        "content_inference": display_or_unknown(row.get("content_inference")),
        "manual_verification": display_or_unknown(row.get("manual_verification")),
        "evidence_sources": combine_text([row.get("evidence_sources"), input_reference]),
        "risk_points": combine_text([row.get("risk_points"), row.get("risk_review_evidence")]),
        "review_status": "pending_review",
        "model_version": VERSION,
    }

    known_positive = 0.0
    known_component_count = 0
    missing_max = 0
    missing_fields: list[str] = []
    for output_field, components in SCORE_GROUPS.items():
        subtotal = 0.0
        complete = True
        for field, maximum in components:
            value = parse_float(row.get(field))
            if value is None or value < 0 or value > maximum:
                complete = False
                missing_fields.append(field)
                missing_max += maximum
            else:
                subtotal += value
                known_positive += value
                known_component_count += 1
        result[output_field] = fmt_number(subtotal) if complete else "unknown"

    risk = parse_float(row.get("risk_deduction"))
    if risk is None or risk < 0 or risk > 20:
        risk = None
        missing_fields.append("risk_deduction")
    else:
        known_component_count += 1
    result["risk_deduction"] = fmt_number(risk)
    result["known_positive_score"] = fmt_number(known_positive) if known_component_count else "unknown"
    result["missing_data"] = "|".join(missing_fields) if missing_fields else "none"
    result["evidence_coverage_pct"] = fmt_number(known_component_count / TOTAL_EVIDENCE_COMPONENTS * 100)
    minimum_risk = risk if risk is not None else 0
    maximum_risk = risk if risk is not None else 20
    possible_min = max(0.0, known_positive - maximum_risk)
    possible_max = min(100.0, known_positive + missing_max - minimum_risk)
    result["possible_score_range"] = f"{fmt_number(possible_min)}-{fmt_number(possible_max)}"

    if not missing_fields:
        positive = known_positive
        total = max(0.0, min(100.0, positive - float(risk or 0)))
        grade = score_label(total) if scoring_model_approved else "待确认模型"
        score_status = "complete" if scoring_model_approved else "complete_unapproved"
        result.update(positive_score=fmt_number(positive), total_score=fmt_number(total), grade=grade, score_status=score_status)
    else:
        grade = "待补数"
        result.update(positive_score="unknown", total_score="待补数", grade=grade, score_status="incomplete")

    strategy, _reason = strategy_for(row)
    result["recommended_strategy"] = strategy
    actions = {
        "A": ("优先建联候选", "复核最近 10–20 条内容、评论和商务条件后审批首条消息"),
        "B": ("标准建联候选", "核验至少一个真实内容匹配点和商务条件后审批首条消息"),
        "C": ("观察/补充证据", "补充人群或带货证据，暂不生成邀约"),
        "D": ("暂缓", "保留在达人库，除非活动目标变化否则不建联"),
        "待确认模型": ("候选评分", "先由用户批准本次 Campaign 的评分模型，再进行正式分级或生成邀约"),
        "待补数": ("待补数", "进入人工复核队列，补齐 missing_data 中的证据后重新运行"),
    }
    result["recommendation"], result["next_action"] = actions[grade]
    result["manual_calibration_sample"] = "false"
    result["_source_row"] = row
    return result


def offer_is_confirmed(config: dict[str, Any]) -> bool:
    offer = config.get("offer", {})
    return isinstance(offer, dict) and offer.get("confirmed") is True


def first_name(row: dict[str, str]) -> str:
    nickname = text_value(row.get("nickname"))
    return display_or_unknown(row.get("creator_handle")) if is_unknown(nickname) else nickname


def observation_for(row: dict[str, str]) -> tuple[str, bool]:
    observation = text_value(row.get("recent_content_observation"))
    verified = parse_bool(row.get("personalization_verified")) is True
    if is_unknown(observation) or not verified:
        return "[需人工补充并核验一条近期内容观察]", True
    return observation, False


def build_draft(scored: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    row = scored["_source_row"]
    name = first_name(row)
    brand = display_or_unknown(config.get("brand"))
    product = display_or_unknown(config.get("product_name"))
    value = display_or_unknown(config.get("one_sentence_value"))
    observation, needs_verification = observation_for(row)
    strategy, strategy_reason = strategy_for(row)
    offer_note = "合作条件将在人工审核后确认" if not offer_is_confirmed(config) else "可按已审批的活动条件进一步沟通"
    language = canonical_language(row.get("language"))

    if language == "id":
        dm = f"Hai {name}, saya dari {brand}. Saya melihat konten Anda: {observation}. Cara Anda menjelaskan rutinitas terasa relevan dengan {product}. Kami ingin mengeksplorasi kolaborasi skala kecil; {offer_note}. Apakah Anda terbuka untuk melihat brief singkatnya?"
        subject = f"Potensi kolaborasi {brand} × {name}"
        body = f"Hai {name},\n\nSaya menghubungi Anda dari {brand}. Observasi kami: {observation}. Kami melihat kecocokan dengan {product}: {value}. Kami menyarankan {strategy}; {offer_note}. Jika tertarik, kami dapat mengirim brief untuk Anda tinjau tanpa kewajiban.\n\nSalam,\nCampaign team"
        follow = f"Hai {name}, izin follow up singkat mengenai kemungkinan kolaborasi {product}. Jika belum relevan, beri tahu kami dan kami tidak akan menghubungi lagi."
        sample = f"Terima kasih, {name}. Sampel belum dijanjikan. Tim perlu mengonfirmasi alamat, wilayah pengiriman, dan persetujuan internal sebelum pengiriman."
    elif language == "zh":
        dm = f"你好 {name}，我是 {brand} 团队。我们留意到你最近的内容：{observation}。你的表达方式与 {product} 的使用场景很契合。我们想先探讨一次小规模合作，{offer_note}。方便先看一份简短 Brief 吗？"
        subject = f"{brand} × {name} 合作探讨"
        body = f"你好 {name}：\n\n我们来自 {brand}。我们注意到：{observation}。这与 {product} 的核心价值“{value}”有较好的内容匹配。当前建议合作方式为“{strategy}”，{offer_note}。如果你有兴趣，我们可以先发送 Brief 供你无压力评估。\n\nCampaign team"
        follow = f"你好 {name}，简短跟进一下 {product} 的合作邀请。如果目前不合适，请直接告诉我们，我们会停止跟进。"
        sample = f"谢谢你，{name}。目前不承诺寄样；团队需先确认地址、配送区域和内部审批，通过后再同步物流安排。"
    else:
        dm = f"Hi {name} — I’m with {brand}. I noticed your recent content: {observation}. Your way of explaining routines looks relevant to {product}. We’d like to explore a small test; {offer_note}. Would you be open to reviewing a short brief?"
        subject = f"Potential {brand} × {name} collaboration"
        body = f"Hi {name},\n\nI’m reaching out from {brand}. We noticed: {observation}. That looks relevant to {product}, whose core value is: {value}. Our current strategy suggestion is {strategy}; {offer_note}. If this sounds relevant, we can send a short brief for a no-pressure review.\n\nBest,\nCampaign team"
        follow = f"Hi {name}, just following up on the possible {product} collaboration. If it is not relevant, let us know and we will stop following up."
        sample = f"Thanks, {name}. A sample is not promised yet; the team must confirm address eligibility, shipping region, and internal approval before dispatch."
    return {
        "creator_handle": scored["creator_handle"], "nickname": scored["nickname"],
        "grade": scored["grade"], "total_score": scored["total_score"],
        "recommended_strategy": strategy, "strategy_reason": strategy_reason, "tiktok_dm": dm,
        "email_subject": subject, "email_body": body, "follow_up_48_72h": follow,
        "sample_communication": sample,
        "draft_readiness": "needs_content_verification" if needs_verification else "ready_for_human_approval",
        "personalization_needs_verification": "true" if needs_verification else "false",
        "review_status": "pending_review", "send_status": "NOT_SENT",
        "contact_status": "pending_review", "message_version": VERSION,
    }


def missing_rates(rows: list[dict[str, str]]) -> dict[str, float]:
    if not rows:
        return {field: 1.0 for field in QUALITY_FIELDS}
    return {field: round(sum(1 for row in rows if is_unknown(row.get(field))) / len(rows), 4) for field in QUALITY_FIELDS}


def ranked_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    grade_order = {"A": 0, "B": 1, "C": 2, "D": 3, "待确认模型": 4, "待补数": 5}
    return (
        grade_order.get(str(item["grade"]), 9),
        -(parse_float(item.get("total_score")) or -1),
        -parse_float(item.get("evidence_coverage_pct")) if parse_float(item.get("evidence_coverage_pct")) is not None else 0,
        normalize_handle(item.get("creator_handle")),
    )


def review_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    grade = str(item.get("grade"))
    group = 0 if grade in {"A", "B"} else 1 if grade == "待补数" else 2 if grade == "C" else 3
    row = item["_source_row"]
    metric_coverage = sum(
        not is_unknown(row.get(field))
        for field in ["recent_views", "engagement_rate_pct", "authorized_gmv", "units_sold", "avg_shoppable_video_views", "audience_profile"]
    )
    views = parse_float(item.get("recent_views_median")) or -1
    engagement = parse_float(item.get("engagement_rate_pct")) or -1
    followers = parse_float(item.get("followers")) or -1
    return (
        group,
        -(parse_float(item.get("total_score")) or -1),
        -(parse_float(item.get("evidence_coverage_pct")) or 0),
        -metric_coverage,
        -views,
        -engagement,
        -followers,
        normalize_handle(item.get("creator_handle")),
    )


def selection_reason(item: dict[str, Any]) -> str:
    if item["grade"] in {"A", "B"}:
        return f"完整评分 {item['grade']} 级，总分 {item['total_score']}，进入优先人工复核。"
    if item["grade"] == "待补数":
        signals = [f"证据覆盖 {item['evidence_coverage_pct']}%"]
        if not is_unknown(item.get("recent_views_median")):
            signals.append(f"近期播放中位数 {item['recent_views_median']}")
        if not is_unknown(item.get("engagement_rate_pct")):
            engagement = text_value(item["engagement_rate_pct"])
            signals.append(f"互动率 {engagement if '%' in engagement or '％' in engagement else engagement + '%'}")
        return "待补数；" + "；".join(signals) + "。该排序仅决定复核先后，不是原版最终分。"
    return f"已有完整 {item['grade']} 级评分；用于校准或补充复核。"


def build_queue(items: list[dict[str, Any]], limit: int, stage: str) -> list[dict[str, Any]]:
    selected = sorted(items, key=review_sort_key)[: max(0, limit)]
    rows: list[dict[str, Any]] = []
    for priority, item in enumerate(selected, start=1):
        source = item["_source_row"].copy()
        output: dict[str, Any] = {
            "queue_priority": priority,
            "selection_stage": stage,
            "selection_reason": selection_reason(item),
            "current_grade": item["grade"],
            "current_total_score": item["total_score"],
            "evidence_coverage_pct": item["evidence_coverage_pct"],
            "missing_data": item["missing_data"],
            "recommended_video_review_count": "10-20" if stage == "deep_review" else "0-10",
            "deep_review_status": "pending_content_review" if stage == "deep_review" else "pending_standard_review",
            "source_row_number": item["row_number"],
            "source_sheet": item["source_sheet"],
        }
        for field in CANONICAL_INPUT_FIELDS:
            output[field] = source.get(field, "")
        rows.append(output)
    return rows


def analyze(
    input_path: Path, config: dict[str, Any], sheet_name: str | None, header_row: int | None,
    mapping_path: Path | None, standard_limit_override: int | None, deep_limit_override: int | None,
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], list[dict[str, Any]], list[Issue], dict[str, Any], dict[str, Any],
]:
    _headers, raw_rows, mapping_metadata = read_table(input_path, sheet_name, header_row, mapping_path)
    issues: list[Issue] = []
    normalized: list[dict[str, Any]] = []
    ranked: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    seen_handles: set[str] = set()
    seen_urls: set[str] = set()
    duplicate_count = 0
    derived_medians = 0
    scoring_model_approved = config.get("scoring_model_approved") is True

    prepared_rows: list[dict[str, str]] = []
    for raw in raw_rows:
        row, handle_was_derived = prepare_row(raw)
        row_number = parse_int(row.get("_source_row_number")) or 0
        validate_row(row, row_number, issues, handle_was_derived)
        prepared_rows.append(row)
        normalized.append({
            "source_row_number": row_number,
            "source_sheet": row.get("_source_sheet", "unknown"),
            **{field: row.get(field, "") for field in CANONICAL_INPUT_FIELDS},
        })

        handle_key = normalize_handle(row.get("creator_handle"))
        url_key = normalize_url(row.get("creator_url"))
        duplicate = bool((handle_key and handle_key in seen_handles) or (url_key and url_key in seen_urls))
        if duplicate:
            duplicate_count += 1
            add_issue(issues, row_number, display_or_unknown(row.get("creator_handle")), "error", "creator_handle/creator_url", "duplicate", "与前一条记录重复。", "核对后保留证据更完整的一条。")
            excluded.append({"row_number": row_number, "creator_handle": display_or_unknown(row.get("creator_handle")), "creator_url": display_or_unknown(row.get("creator_url")), "exclusion_reasons": "duplicate_handle_or_url"})
            continue
        if handle_key:
            seen_handles.add(handle_key)
        if url_key:
            seen_urls.add(url_key)
        views, _bad = split_views(row.get("recent_views"))
        if views:
            derived_medians += 1
        reasons = hard_filter_reasons(row, config)
        if reasons:
            excluded.append({"row_number": row_number, "creator_handle": display_or_unknown(row.get("creator_handle")), "creator_url": display_or_unknown(row.get("creator_url")), "exclusion_reasons": ";".join(reasons)})
            continue
        ranked.append(score_row(row, row_number, scoring_model_approved))

    ranked.sort(key=ranked_sort_key)
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
    if ranked:
        seed_text = text_value(config.get("campaign_name")) + "|" + "|".join(item["creator_handle"] for item in ranked)
        seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        calibration_indices = set(rng.sample(range(len(ranked)), k=min(10, len(ranked))))
        for index, item in enumerate(ranked):
            item["manual_calibration_sample"] = "true" if index in calibration_indices else "false"

    funnel = config.get("funnel", {}) if isinstance(config.get("funnel"), dict) else {}
    standard_limit = standard_limit_override if standard_limit_override is not None else (parse_int(funnel.get("standard_review_limit")) or 100)
    deep_limit = deep_limit_override if deep_limit_override is not None else (parse_int(funnel.get("deep_review_limit")) or 40)
    standard_queue = build_queue(ranked, standard_limit, "standard_review")
    deep_queue = build_queue(ranked, min(deep_limit, standard_limit), "deep_review")
    drafts = [build_draft(item, config) for item in ranked if item["grade"] in {"A", "B"}]
    complete_scores = [item for item in ranked if item["score_status"] in {"complete", "complete_unapproved"}]
    quality = {
        "model_version": VERSION,
        "scoring_model_approved": scoring_model_approved,
        "input_file": str(input_path.resolve()),
        "input_format": mapping_metadata["input_format"],
        "selected_sheet": mapping_metadata["selected_sheet"],
        "header_row": mapping_metadata["header_row"],
        "input_rows": len(raw_rows),
        "valid_identity_rows": sum(1 for row in prepared_rows if not is_unknown(row.get("creator_handle"))),
        "ranked_rows": len(ranked),
        "excluded_rows": len(excluded),
        "duplicate_rows": duplicate_count,
        "missing_rates": missing_rates(prepared_rows),
        "issue_counts": dict(Counter(item.severity for item in issues)),
        "derived_values": {"recent_views_median_rows": derived_medians},
        "complete_score_rows": len(complete_scores),
        "incomplete_score_rows": len(ranked) - len(complete_scores),
        "grade_counts": dict(Counter(item["grade"] for item in ranked)),
        "calibration_sample_handles": [item["creator_handle"] for item in ranked if item["manual_calibration_sample"] == "true"],
        "standard_review_queue_rows": len(standard_queue),
        "deep_review_queue_rows": len(deep_queue),
        "draft_rows": len(drafts),
        "api_calls": 0,
        "paid_data_sources": "none",
        "external_actions": "none",
    }
    return normalized, ranked, excluded, standard_queue, deep_queue, drafts, issues, quality, mapping_metadata


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def report_markdown(
    config: dict[str, Any], ranked: list[dict[str, Any]], excluded: list[dict[str, Any]],
    standard_queue: list[dict[str, Any]], deep_queue: list[dict[str, Any]], drafts: list[dict[str, Any]],
    quality: dict[str, Any], mapping_metadata: dict[str, Any],
) -> str:
    grade_counts = quality.get("grade_counts", {})
    lines = [
        "# TikTok 达人筛选与建联准备报告", "",
        f"- Campaign：{display_or_unknown(config.get('campaign_name'))}",
        f"- 产品：{display_or_unknown(config.get('product_name'))}",
        f"- 目标市场/语言：{display_or_unknown(config.get('market'))} / {', '.join(config.get('languages', [])) or 'unknown'}",
        f"- 模型版本：{VERSION}",
        f"- 输入：{mapping_metadata['input_format'].upper()} / {mapping_metadata['selected_sheet']} / 表头第 {mapping_metadata['header_row']} 行。",
        f"- 输入 {quality['input_rows']} 行；进入评分 {len(ranked)}；硬筛排除 {len(excluded)}；标准复核 {len(standard_queue)}；深度复核 {len(deep_queue)}；草稿 {len(drafts)}。",
        f"- 分级：A {grade_counts.get('A', 0)} / B {grade_counts.get('B', 0)} / C {grade_counts.get('C', 0)} / D {grade_counts.get('D', 0)} / 待确认模型 {grade_counts.get('待确认模型', 0)} / 待补数 {grade_counts.get('待补数', 0)}。",
        f"- 评分模型批准：{'是' if quality.get('scoring_model_approved') else '否；当前得分只作候选分析，不生成正式等级或邀约草稿'}。",
        f"- 表头映射 {len(mapping_metadata.get('mapped_columns', []))} 列；未映射 {len(mapping_metadata.get('unmapped_source_columns', []))} 列。",
        "- 成本边界：本次只读取本地导表；API 调用 0，付费数据源 0。",
        "- 安全边界：没有抓取、发送消息、创建会话、寄样或修改商务条件。", "",
        "## 优先候选", "",
        "| Rank | Creator | Grade | Total | Coverage | Next action |",
        "|---:|---|:---:|---:|---:|---|",
    ]
    for item in ranked[:20]:
        lines.append(f"| {item['rank']} | {item['creator_handle']} | {item['grade']} | {item['total_score']} | {item['evidence_coverage_pct']}% | {item['next_action']} |")
    if not ranked:
        lines.append("| - | 无 | - | - | - | 检查排除清单和身份字段映射 |")
    lines += ["", "## 人工复核", ""]
    lines.append("`deep_review_queue.csv` 已预留最近 10–20 条视频、Hook、产品演示、表达、制作、稳定性和评论购买意向证据字段。填完后可作为新输入再次运行；只有本次 Campaign 明确设置 `scoring_model_approved=true`，才生成正式 A/B/C/D 分级和 A/B 待审核草稿。")
    lines += ["", "## 输出文件", "",
        "- `normalized_creators.csv`：自动映射后的规范字段，不覆盖原始导出。",
        "- `ranked_creators.csv`：原版四维评分、证据覆盖率和下一步动作。",
        "- `standard_review_queue.csv`：默认前 100 位标准复核队列。",
        "- `deep_review_queue.csv`：默认前 40 位的 10–20 条视频/评论深度复核表。",
        "- `outreach_drafts.csv`：仅完整 A/B 候选的待审核草稿。",
        "- `excluded_creators.csv`：硬筛和重复记录。",
        "- `header_mapping.json`、`data_issues.csv`、`data_quality.json`：字段映射与数据体检。",
    ]
    return "\n".join(lines) + "\n"


def run_command(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    config = load_config(Path(args.config))
    output_dir = Path(args.output_dir)
    result = analyze(
        input_path, config, args.sheet, args.header_row, Path(args.mapping) if args.mapping else None,
        args.standard_review_limit, args.deep_review_limit,
    )
    normalized, ranked, excluded, standard_queue, deep_queue, drafts, issues, quality, mapping_metadata = result
    output_dir.mkdir(parents=True, exist_ok=True)
    public_ranked = [{key: value for key, value in item.items() if not key.startswith("_")} for item in ranked]
    write_csv(output_dir / "normalized_creators.csv", NORMALIZED_FIELDS, normalized)
    write_csv(output_dir / "ranked_creators.csv", RANKED_FIELDS, public_ranked)
    write_csv(output_dir / "excluded_creators.csv", ["row_number", "creator_handle", "creator_url", "exclusion_reasons"], excluded)
    write_csv(output_dir / "standard_review_queue.csv", QUEUE_PREFIX_FIELDS + CANONICAL_INPUT_FIELDS, standard_queue)
    write_csv(output_dir / "deep_review_queue.csv", QUEUE_PREFIX_FIELDS + CANONICAL_INPUT_FIELDS, deep_queue)
    write_csv(output_dir / "outreach_drafts.csv", DRAFT_FIELDS, drafts)
    write_csv(output_dir / "data_issues.csv", list(Issue.__dataclass_fields__.keys()), [item.as_dict() for item in issues])
    for filename, data in [("data_quality.json", quality), ("header_mapping.json", mapping_metadata)]:
        with (output_dir / filename).open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    with (output_dir / "analysis_report.md").open("w", encoding="utf-8") as handle:
        handle.write(report_markdown(config, ranked, excluded, standard_queue, deep_queue, drafts, quality, mapping_metadata))
    print(json.dumps({"output_dir": str(output_dir.resolve()), **quality}, ensure_ascii=False, indent=2))
    return 0


def validate_command(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    _headers, raw_rows, mapping_metadata = read_table(
        input_path, args.sheet, args.header_row, Path(args.mapping) if args.mapping else None,
    )
    issues: list[Issue] = []
    prepared: list[dict[str, str]] = []
    for raw in raw_rows:
        row, derived = prepare_row(raw)
        prepared.append(row)
        validate_row(row, parse_int(row.get("_source_row_number")) or 0, issues, derived)
    result = {
        "valid": not any(item.severity == "error" for item in issues),
        "input_rows": len(prepared),
        "input_format": mapping_metadata["input_format"],
        "selected_sheet": mapping_metadata["selected_sheet"],
        "header_row": mapping_metadata["header_row"],
        "missing_rates": missing_rates(prepared),
        "issue_counts": dict(Counter(item.severity for item in issues)),
        "unmapped_source_columns": mapping_metadata["unmapped_source_columns"],
        "issues": [item.as_dict() for item in issues],
        "api_calls": 0,
        "paid_data_sources": "none",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 2


def add_table_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", required=True, help="Authorized creator .csv, .tsv, or .xlsx export")
    parser.add_argument("--sheet", help="XLSX worksheet name; auto-detected when omitted")
    parser.add_argument("--header-row", type=int, help="One-based header row; auto-detected when omitted")
    parser.add_argument("--mapping", help="Optional JSON mapping for provider-specific source headers")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local TikTok creator outreach preparation from authorized exports; no API and no sending")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Map, validate, filter, score, and generate review queues/drafts")
    add_table_options(run_parser)
    run_parser.add_argument("--config", required=True, help="Campaign config JSON")
    run_parser.add_argument("--output-dir", required=True, help="Directory for generated review files")
    run_parser.add_argument("--standard-review-limit", type=int, help="Override standard review queue size")
    run_parser.add_argument("--deep-review-limit", type=int, help="Override deep review queue size")
    run_parser.set_defaults(func=run_command)
    validate_parser = subparsers.add_parser("validate", help="Validate and map a CSV/XLSX without scoring or drafting")
    add_table_options(validate_parser)
    validate_parser.set_defaults(func=validate_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
