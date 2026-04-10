"""Build the FastAPI/Jinja content into a pure static dist folder."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = BASE_DIR / "dist"
TEMPLATE_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"
IMG_DIR = BASE_DIR / "img"
DATA_FILE = BASE_DIR / "app" / "data" / "site_content.json"


def static_url(path: str) -> str:
    """Return a static asset URL for generated pages."""
    return f"/static/{path}"


def gallery_url(path: str) -> str:
    """Return a gallery asset URL for generated pages."""
    return f"/gallery/{path}"


class StaticURLFor:
    """Small helper that mimics FastAPI's url_for in Jinja templates."""

    def __call__(self, name: str, **kwargs: str) -> str:
        path = kwargs.get("path", "")
        if name == "static":
            return static_url(path)
        if name == "gallery":
            return gallery_url(path)
        return f"/{path}"


def load_json() -> dict[str, Any]:
    """Load site content from JSON."""
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def logo_filename() -> str:
    """Return the event logo filename."""
    for path in sorted(IMG_DIR.glob("*")):
        if path.is_file() and "標誌" in path.stem:
            return path.name
    return "backgroud.png"


def gallery_photos() -> list[dict[str, str | int]]:
    """Return gallery metadata."""
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
    """Load the charter text file."""
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


def write_page(env: Environment, template_name: str, output_path: Path, context: dict[str, Any]) -> None:
    """Render a template and write it to dist."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = env.get_template(template_name)
    html = template.render(
        app_name="Xindian_Cup",
        logo_filename=logo_filename(),
        url_for=StaticURLFor(),
        static_site=True,
        **context,
    )
    output_path.write_text(html, encoding="utf-8")


def copy_assets() -> None:
    """Copy static and gallery assets into dist."""
    shutil.copytree(STATIC_DIR, DIST_DIR / "static", dirs_exist_ok=True)
    shutil.copytree(IMG_DIR, DIST_DIR / "gallery", dirs_exist_ok=True)


def build() -> None:
    """Build the static site."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    content = load_json()

    write_page(
        env,
        "index.html",
        DIST_DIR / "index.html",
        {
            "hero_title": content["hero_title"],
            "hero_subtitle": content["hero_subtitle"],
            "hero_description": content["hero_description"],
            "team_count": len(content["teams"]),
        },
    )
    write_page(env, "line_login.html", DIST_DIR / "line" / "login" / "index.html", {"error_message": None, "allowed_ids_configured": False})
    write_page(env, "public_teams.html", DIST_DIR / "public" / "teams" / "index.html", {"teams": content["teams"]})
    write_page(env, "schedule.html", DIST_DIR / "schedule" / "index.html", {"schedule": content["schedule"]})
    write_page(env, "history_gallery.html", DIST_DIR / "history" / "photos" / "index.html", {"gallery_photos": gallery_photos()})
    write_page(env, "charter.html", DIST_DIR / "charter" / "index.html", {"charter": load_charter()})
    copy_assets()
    print(f"Static site built: {DIST_DIR}")


if __name__ == "__main__":
    build()
