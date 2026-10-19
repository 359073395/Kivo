#!/usr/bin/env python3
import argparse
import os
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme != "https" or parsed.hostname not in {"dxmdl.dianxiaomi.com"}:
        raise SystemExit("只允许从店小秘 HTTPS 下载域名安装导出文件")

    root = Path(args.root).resolve()
    target = Path(args.target).resolve()
    if root not in target.parents:
        raise SystemExit("目标文件不在固定产品库根目录内")
    if not target.is_file():
        raise SystemExit("目标产品表不存在；禁止新建文件")
    if target.name.casefold() == "flash deal.xlsx":
        raise SystemExit("禁止覆盖 Flash Deal.xlsx")
    if target.suffix.casefold() != ".xlsx":
        raise SystemExit("目标必须是 .xlsx")

    fd, temp_name = tempfile.mkstemp(prefix=".dianxiaomi-update-", suffix=".xlsx", dir=target.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        request = urllib.request.Request(args.url, headers={"User-Agent": "Codex-Dianxiaomi-Updater/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, temp_path.open("wb") as output:
            output.write(response.read())
        if temp_path.stat().st_size < 4 or temp_path.read_bytes()[:2] != b"PK":
            raise ValueError("下载内容不是有效的 XLSX ZIP 文件")
        with zipfile.ZipFile(temp_path) as archive:
            if archive.testzip() is not None:
                raise ValueError("下载的 XLSX 已损坏")
            required = {"xl/workbook.xml", "[Content_Types].xml"}
            if not required.issubset(set(archive.namelist())):
                raise ValueError("下载文件缺少 XLSX 必需结构")
        os.replace(temp_path, target)
        print(str(target))
    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    main()

