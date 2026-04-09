"""FastAPI application entrypoint."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.router import api_router
from app.core.config import get_settings
from app.models.member import Member
from app.models.team import Team, TeamStatus
from app.services.auth import get_captain_session_by_token, is_team_email_verified
from app.services.security import generate_token, hash_token

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "img"
CAPTAIN_SESSION_COOKIE = "captain_session"

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/gallery", StaticFiles(directory="img"), name="gallery")
templates = Jinja2Templates(directory="app/templates")


def get_logo_filename() -> str:
    """Return the event logo filename from the img directory."""
    for path in sorted(IMG_DIR.glob("*")):
        if path.is_file() and "標誌" in path.stem:
            return path.name
    return "backgroud.png"


def get_gallery_photos() -> list[dict[str, str | int]]:
    """Return curated gallery metadata for event pages sorted by year."""
    photos = [
        {
            "year": "2012",
            "sort_year": 2012,
            "sort_order": 1,
            "file": "2012.jpg",
            "caption": "校友與在校生齊聚開打，留下第一批珍貴合照。",
        },
        {
            "year": "2013",
            "sort_year": 2013,
            "sort_order": 1,
            "file": "2013.jpg",
            "caption": "比賽規模逐步穩定，隊伍間的交流也更熱絡。",
        },
        {
            "year": "2014",
            "sort_year": 2014,
            "sort_order": 1,
            "file": "2014.jpg",
            "caption": "場上節奏更加成熟，延續新店盃的熱血氣氛。",
        },
        {
            "year": "2018",
            "sort_year": 2018,
            "sort_order": 1,
            "file": "2018.jpg",
            "caption": "經過幾年累積，活動現場已成為校友相見的重要時刻。",
        },
        {
            "year": "2019",
            "sort_year": 2019,
            "sort_order": 1,
            "file": "2019.jpg",
            "caption": "比賽與聚會並行，場邊也充滿歡呼與加油聲。",
        },
        {
            "year": "2020",
            "sort_year": 2020,
            "sort_order": 1,
            "file": "2020.jpg",
            "caption": "延續賽事傳統，讓新舊世代球友持續在場上相遇。",
        },
        {
            "year": "2022",
            "sort_year": 2022,
            "sort_order": 1,
            "file": "2022.jpg",
            "caption": "回歸賽場的熱度更高，整體氛圍也更完整。",
        },
        {
            "year": "2022",
            "sort_year": 2022,
            "sort_order": 2,
            "file": "2022_1.jpg",
            "caption": "從團體照到比賽瞬間，都記錄下新店盃的重要年份。",
        },
        {
            "year": "2024",
            "sort_year": 2024,
            "sort_order": 1,
            "file": "2024.png",
            "caption": "最新一屆影像加入後，歷屆紀錄更加完整。",
        },
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


def _render_captain_manage_page(
    request: Request,
    db: Session,
    *,
    status_code: int = 200,
    access_denied: str | None = None,
    flash_message: str | None = None,
    verification_preview_url: str | None = None,
) -> HTMLResponse:
    """Render the captain management page from the session cookie when available."""
    session_token = request.cookies.get(CAPTAIN_SESSION_COOKIE)
    captain_session = None
    team = None
    members: list[Member] = []
    email_verified = False

    if session_token:
        try:
            captain_session, team = get_captain_session_by_token(db, session_token)
            stmt = (
                select(Member)
                .where(Member.team_id == team.id)
                .order_by(Member.created_at, Member.id)
            )
            members = list(db.scalars(stmt).all())
            email_verified = is_team_email_verified(db, team.id)
        except Exception as exc:  # noqa: BLE001
            access_denied = str(exc.detail) if hasattr(exc, "detail") else "隊長登入狀態已失效。"
            captain_session = None
            team = None

    return templates.TemplateResponse(
        request,
        "captain_manage.html",
        {
            "app_name": settings.app_name,
            "logo_filename": get_logo_filename(),
            "team": team,
            "members": members,
            "email_verified": email_verified,
            "access_denied": access_denied,
            "flash_message": flash_message,
            "verification_preview_url": verification_preview_url,
            "captain_session": captain_session,
        },
        status_code=status_code,
    )


def _render_admin_teams_page(
    request: Request,
    *,
    flash_message: str | None = None,
    error_message: str | None = None,
    created_team: Team | None = None,
    form_data: dict[str, str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """Render the admin team creation page."""
    return templates.TemplateResponse(
        request,
        "admin_teams.html",
        {
            "app_name": settings.app_name,
            "logo_filename": get_logo_filename(),
            "flash_message": flash_message,
            "error_message": error_message,
            "created_team": created_team,
            "form_data": form_data or {},
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def index(request: Request) -> HTMLResponse:
    """Render the public event landing page."""
    gallery_photos = get_gallery_photos()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "logo_filename": get_logo_filename(),
            "hero_title": "XINDIAN_CUP",
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
            "logo_filename": get_logo_filename(),
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
            "logo_filename": get_logo_filename(),
            "charter": load_charter(),
        },
    )


@app.get("/captain/manage", response_class=HTMLResponse, tags=["pages"])
async def captain_manage(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Render the captain management page guarded by a LINE-issued session."""
    session_token = request.query_params.get("session_token")
    if session_token:
        response = RedirectResponse(url="/captain/manage", status_code=303)
        response.set_cookie(
            CAPTAIN_SESSION_COOKIE,
            session_token,
            httponly=True,
            samesite="lax",
            max_age=settings.session_expire_hours * 3600,
        )
        return response
    if request.cookies.get(CAPTAIN_SESSION_COOKIE):
        return _render_captain_manage_page(request, db)
    return _render_captain_manage_page(
        request,
        db,
        access_denied="請先完成 LINE 驗證入口，取得隊長管理頁的登入狀態。",
    )


@app.get("/admin/teams", response_class=HTMLResponse, tags=["pages"])
async def admin_teams_page(request: Request) -> HTMLResponse:
    """Render the admin team creation page."""
    return _render_admin_teams_page(request)


@app.post("/admin/teams", response_class=HTMLResponse, tags=["pages"])
async def admin_teams_create(
    request: Request,
    admin_token: str = Form(...),
    team_name: str = Form(...),
    captain_name: str = Form(...),
    captain_email: str = Form(...),
    captain_phone: str | None = Form(default=None),
    captain_line_user_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Create a team from the admin web form."""
    form_data = {
        "team_name": team_name,
        "captain_name": captain_name,
        "captain_email": captain_email,
        "captain_phone": captain_phone or "",
        "captain_line_user_id": captain_line_user_id or "",
    }
    if admin_token != settings.admin_api_token:
        return _render_admin_teams_page(
            request,
            error_message="管理者 token 不正確，無法建立隊伍。",
            form_data=form_data,
            status_code=401,
        )

    team = Team(
        team_name=team_name.strip(),
        captain_name=captain_name.strip(),
        captain_email=captain_email.strip(),
        captain_phone=(captain_phone or "").strip() or None,
        captain_line_user_id=(captain_line_user_id or "").strip() or None,
        status=TeamStatus.PENDING,
    )
    try:
        db.add(team)
        db.commit()
        db.refresh(team)
    except IntegrityError:
        db.rollback()
        return _render_admin_teams_page(
            request,
            error_message="隊伍名稱或隊長 Email 已存在，請換一組再試。",
            form_data=form_data,
            status_code=409,
        )

    return _render_admin_teams_page(
        request,
        flash_message="隊伍與隊長資料已建立完成。",
        created_team=team,
    )


@app.post("/captain/logout", response_class=RedirectResponse, tags=["pages"])
async def captain_logout() -> RedirectResponse:
    """Clear the captain session cookie and return to the landing page."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(CAPTAIN_SESSION_COOKIE)
    return response


@app.post("/captain/manage/send-email-verification", response_class=HTMLResponse, tags=["pages"])
async def captain_manage_send_email_verification(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Issue an email verification link for the captain currently bound to the cookie session."""
    session_token = request.cookies.get(CAPTAIN_SESSION_COOKIE)
    if not session_token:
        return _render_captain_manage_page(
            request,
            db,
            status_code=401,
            access_denied="請先完成 LINE 驗證入口，取得隊長管理頁的登入狀態。",
        )

    _, team = get_captain_session_by_token(db, session_token)
    if is_team_email_verified(db, team.id):
        return _render_captain_manage_page(
            request,
            db,
            flash_message="隊長 Email 已完成驗證。",
        )

    from app.models.email_verification import EmailVerification

    raw_token = generate_token(24)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.email_verification_expire_minutes
    )
    verification = EmailVerification(
        team_id=team.id,
        email=team.captain_email,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )
    db.add(verification)
    db.commit()

    preview_url = f"{settings.app_base_url}/captain/verify-email?token={raw_token}"
    return _render_captain_manage_page(
        request,
        db,
        flash_message="測試環境已建立 Email 驗證連結，請使用下方連結完成驗證。",
        verification_preview_url=preview_url,
    )


@app.get("/captain/verify-email", response_class=HTMLResponse, tags=["pages"])
async def captain_verify_email_page(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Handle email verification links for browser users and return to the captain page."""
    from app.models.email_verification import EmailVerification

    stmt = select(EmailVerification).where(EmailVerification.token_hash == hash_token(token))
    record = db.scalars(stmt).first()
    if record is None:
        return _render_captain_manage_page(
            request,
            db,
            status_code=404,
            access_denied="驗證連結不存在。",
        )
    if record.used_at is not None:
        return _render_captain_manage_page(
            request,
            db,
            flash_message="這組 Email 驗證連結已使用過。",
        )

    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return _render_captain_manage_page(
            request,
            db,
            status_code=400,
            access_denied="驗證連結已過期，請重新申請。",
        )

    record.used_at = datetime.now(timezone.utc)
    team = db.get(Team, record.team_id)
    if team:
        team.status = TeamStatus.ACTIVE
        db.add(team)
    db.add(record)
    db.commit()
    return _render_captain_manage_page(
        request,
        db,
        flash_message="Email 驗證完成，現在可以新增隊員與維護名單。",
    )


@app.post("/captain/manage/members", response_class=HTMLResponse, tags=["pages"])
async def captain_manage_create_member(
    request: Request,
    name: str = Form(...),
    phone: str | None = Form(default=None),
    is_alumni: bool = Form(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Create a member from the protected captain management page."""
    session_token = request.cookies.get(CAPTAIN_SESSION_COOKIE)
    if not session_token:
        return _render_captain_manage_page(
            request,
            db,
            status_code=401,
            access_denied="請先完成 LINE 驗證入口，取得隊長管理頁的登入狀態。",
        )

    captain_session, team = get_captain_session_by_token(db, session_token)
    if not is_team_email_verified(db, team.id):
        return _render_captain_manage_page(
            request,
            db,
            status_code=403,
            access_denied="請先完成隊長 Email 驗證，才可新增隊員。",
        )

    member = Member(
        team_id=team.id,
        name=name.strip(),
        phone=(phone or "").strip() or None,
        is_alumni=is_alumni,
        created_by=captain_session.id,
    )
    db.add(member)
    db.commit()
    return RedirectResponse(url="/captain/manage", status_code=303)


app.include_router(api_router)
