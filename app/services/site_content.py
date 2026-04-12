"""Helpers for loading public site content."""

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
IMG_DIR = BASE_DIR / "img"
DATA_FILE = BASE_DIR / "app" / "data" / "site_content.json"


def get_logo_filename() -> str:
    """Return the first logo-like file from the img directory."""
    for path in sorted(IMG_DIR.glob("*")):
        if path.is_file() and "標誌" in path.stem:
            return path.name
    return "backgroud.png"


def get_gallery_photos() -> list[dict[str, str | int]]:
    """Return gallery metadata for the history page."""
    photos = [
        {"year": "2012", "sort_year": 2012, "sort_order": 1, "file": "2012.jpg", "caption": "初代新店盃合照與賽事紀錄。"},
        {"year": "2013", "sort_year": 2013, "sort_order": 1, "file": "2013.jpg", "caption": "校友交流與比賽氣氛逐漸成形。"},
        {"year": "2014", "sort_year": 2014, "sort_order": 1, "file": "2014.jpg", "caption": "延續每年固定相聚的排球傳統。"},
        {"year": "2018", "sort_year": 2018, "sort_order": 1, "file": "2018.jpg", "caption": "更多不同屆次的校友一起回到球場。"},
        {"year": "2019", "sort_year": 2019, "sort_order": 1, "file": "2019.jpg", "caption": "比賽與聚會並行，留下熱鬧現場。"},
        {"year": "2020", "sort_year": 2020, "sort_order": 1, "file": "2020.jpg", "caption": "持續累積新店盃歷年的精彩影像。"},
        {"year": "2022", "sort_year": 2022, "sort_order": 1, "file": "2022.jpg", "caption": "完整記錄回歸賽場後的比賽氛圍。"},
        {"year": "2022", "sort_year": 2022, "sort_order": 2, "file": "2022_1.jpg", "caption": "團體照與比賽片段一起保留下來。"},
        {"year": "2024", "sort_year": 2024, "sort_order": 1, "file": "2024.png", "caption": "最新加入的歷屆照片檔案。"},
    ]
    return sorted(photos, key=lambda item: (item["sort_year"], item["sort_order"]))


def load_charter() -> dict[str, object]:
    """Load and parse the charter text file from the project root."""
    charter_path = next(iter(sorted(BASE_DIR.glob("*章程*.txt"))), None)
    if charter_path is None:
        return {"title": "比賽章程", "sections": []}

    raw_text = charter_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in raw_text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    title = non_empty_lines[0] if non_empty_lines else "比賽章程"

    sections: list[dict[str, object]] = []
    current_section: dict[str, object] | None = None

    for line in non_empty_lines[1:]:
        if "、" in line and len(line) <= 24:
            current_section = {"heading": line, "items": []}
            sections.append(current_section)
            continue

        if current_section is None:
            current_section = {"heading": "章程內容", "items": []}
            sections.append(current_section)

        current_section["items"].append(line)

    return {"title": title, "sections": sections}


def load_site_content() -> dict[str, Any]:
    """Load public site content from JSON."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))
