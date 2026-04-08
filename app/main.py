"""FastAPI application entrypoint."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/gallery", StaticFiles(directory="img"), name="gallery")
templates = Jinja2Templates(directory="app/templates")


def get_gallery_photos() -> list[dict[str, str | int]]:
    """Return curated gallery metadata for the event pages sorted by year."""
    photos = [
        {"year": "2012", "sort_year": 2012, "sort_order": 1, "file": "2012.jpg", "caption": "歷屆賽事合影"},
        {"year": "2013", "sort_year": 2013, "sort_order": 1, "file": "2013.jpg", "caption": "賽事現場紀錄"},
        {"year": "2014", "sort_year": 2014, "sort_order": 1, "file": "2014.jpg", "caption": "隊伍交流與合照"},
        {"year": "2018", "sort_year": 2018, "sort_order": 1, "file": "2018.jpg", "caption": "新店盃比賽回顧"},
        {"year": "2019", "sort_year": 2019, "sort_order": 1, "file": "2019.jpg", "caption": "年度賽事影像"},
        {"year": "2020", "sort_year": 2020, "sort_order": 1, "file": "2020.jpg", "caption": "競賽與校友重聚"},
        {"year": "2022", "sort_year": 2022, "sort_order": 1, "file": "2022.jpg", "caption": "賽事精彩瞬間"},
        {"year": "2022", "sort_year": 2022, "sort_order": 2, "file": "2022_1.jpg", "caption": "球場熱血紀錄"},
        {"year": "2024", "sort_year": 2024, "sort_order": 1, "file": "2024.png", "caption": "最新一屆賽事照片"},
    ]
    return sorted(photos, key=lambda item: (item["sort_year"], item["sort_order"]))


def load_charter() -> dict[str, object]:
    """Load and parse the charter text file from the project root."""
    charter_path = BASE_DIR / "章程.txt"
    raw_text = charter_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in raw_text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    title = non_empty_lines[0] if non_empty_lines else "新店盃排球賽章程"

    sections: list[dict[str, object]] = []
    current_section: dict[str, object] | None = None

    for line in non_empty_lines[1:]:
        if "：" in line and len(line) <= 24:
            current_section = {"heading": line, "items": []}
            sections.append(current_section)
            continue

        if current_section is None:
            current_section = {"heading": "章程內容", "items": []}
            sections.append(current_section)

        current_section["items"].append(line)

    return {"title": title, "sections": sections}


@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def index(request: Request) -> HTMLResponse:
    """Render the public event landing page."""
    gallery_photos = get_gallery_photos()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "hero_title": "Xindian_Cup",
            "hero_subtitle": "新店盃排球賽報名與公告平台",
            "gallery_preview": gallery_photos[-3:],
        },
    )


@app.get("/history/photos", response_class=HTMLResponse, tags=["pages"])
async def history_photos(request: Request) -> HTMLResponse:
    """Render the dedicated history gallery page."""
    return templates.TemplateResponse(
        request,
        "history_gallery.html",
        {
            "app_name": settings.app_name,
            "gallery_photos": get_gallery_photos(),
        },
    )


@app.get("/charter", response_class=HTMLResponse, tags=["pages"])
async def charter_page(request: Request) -> HTMLResponse:
    """Render the event charter page from the root text file."""
    return templates.TemplateResponse(
        request,
        "charter.html",
        {
            "app_name": settings.app_name,
            "charter": load_charter(),
        },
    )


@app.get("/captain/manage", response_class=HTMLResponse, tags=["pages"])
async def captain_manage(request: Request) -> HTMLResponse:
    """Render a temporary captain entry page placeholder."""
    return templates.TemplateResponse(
        request,
        "captain_manage.html",
        {"app_name": settings.app_name},
    )


app.include_router(api_router)
