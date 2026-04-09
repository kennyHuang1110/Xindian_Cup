"""Basic smoke tests for the application."""

from app.api.deps import get_db
from app.main import app
from app.models.email_verification import EmailVerification
from app.services.security import hash_token


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "XINDIAN_CUP" in response.text
    assert "查看公告名單" in response.text


def test_history_and_charter_pages_render(client) -> None:
    history_response = client.get("/history/photos")
    assert history_response.status_code == 200
    assert "歷屆照片" in history_response.text
    assert "2024" in history_response.text

    charter_response = client.get("/charter")
    assert charter_response.status_code == 200
    assert "2026 新店盃混排校友賽" in charter_response.text
    assert "壹、主旨" in charter_response.text


def test_admin_create_team_sets_pending_status(client, admin_headers) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Riverside Shooters",
            "captain_name": "Alice",
            "captain_email": "alice@example.com",
            "captain_phone": "0912345678",
            "captain_line_user_id": "line-alice",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["team_name"] == "Riverside Shooters"
    assert payload["status"] == "pending"


def test_public_teams_page_shows_active_team_and_members(client, admin_headers) -> None:
    team_response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Active Team",
            "captain_name": "Bob",
            "captain_email": "bob@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-bob",
        },
        headers=admin_headers,
    )
    team_id = team_response.json()["id"]

    line_entry_response = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-bob"},
    )
    assert line_entry_response.status_code == 200
    session_token = line_entry_response.json()["session_token"]
    headers = {"Authorization": f"Bearer {session_token}"}

    verification_response = client.post(
        "/api/captain/send-email-verification",
        json={"team_id": team_id, "email": "bob@example.com"},
        headers=headers,
    )
    assert verification_response.status_code == 200
    assert "verification_token" not in verification_response.json()

    member_response = client.post(
        "/api/captain/members",
        json={
            "team_id": team_id,
            "name": "Charlie",
            "phone": "0987654321",
            "is_alumni": True,
            "created_by": 1,
        },
    )
    assert member_response.status_code == 401

    override = app.dependency_overrides[get_db]
    db_generator = override()
    db = next(db_generator)
    record = db.query(EmailVerification).filter(EmailVerification.team_id == team_id).first()
    verification_token = "test-token-bob-001"
    record.token_hash = hash_token(verification_token)
    db.add(record)
    db.commit()
    db.close()

    verify_response = client.get(f"/api/captain/verify-email?token={verification_token}")
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "verified"

    me_response = client.get("/api/captain/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["team_name"] == "Active Team"

    member_response = client.post(
        "/api/captain/members",
        json={
            "team_id": team_id,
            "name": "Charlie",
            "phone": "0987654321",
            "is_alumni": True,
            "created_by": 1,
        },
        headers=headers,
    )
    assert member_response.status_code == 201

    list_members_response = client.get("/api/captain/members", headers=headers)
    assert list_members_response.status_code == 200
    assert list_members_response.json()[0]["name"] == "Charlie"

    api_response = client.get("/api/public/teams")
    assert api_response.status_code == 200
    assert api_response.json()[0]["team_name"] == "Active Team"

    page_response = client.get("/public/teams")
    assert page_response.status_code == 200
    assert "Active Team" in page_response.text
    assert "Charlie" in page_response.text


def test_line_entry_rejects_mismatched_line_user(client, admin_headers) -> None:
    team_response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Mismatch Team",
            "captain_name": "Dana",
            "captain_email": "dana@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-dana",
        },
        headers=admin_headers,
    )
    team_id = team_response.json()["id"]

    line_entry_response = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-someone-else"},
    )
    assert line_entry_response.status_code == 403


def test_admin_endpoints_require_token(client) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "No Admin Team",
            "captain_name": "Eve",
            "captain_email": "eve@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-eve",
        },
    )
    assert response.status_code == 401


def test_line_entry_allows_pending_team_and_manage_page_requires_session(client, admin_headers) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Pending Team",
            "captain_name": "Frank",
            "captain_email": "frank@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-frank",
        },
        headers=admin_headers,
    )
    team_id = response.json()["id"]

    denied_page = client.get("/captain/manage")
    assert denied_page.status_code == 200
    assert "LINE" in denied_page.text

    line_entry = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-frank"},
    )
    assert line_entry.status_code == 200
    assert line_entry.json()["team_status"] == "pending"
    assert "/captain/manage?session_token=" in line_entry.json()["manage_url"]

    manage_page = client.get(line_entry.json()["manage_url"], follow_redirects=True)
    assert manage_page.status_code == 200
    assert "Pending Team" in manage_page.text
    assert "寄送 Email 驗證連結" in manage_page.text


def test_captain_manage_web_flow_adds_member_after_email_verification(client, admin_headers) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Web Manage Team",
            "captain_name": "Grace",
            "captain_email": "grace@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-grace",
        },
        headers=admin_headers,
    )
    team_id = response.json()["id"]

    line_entry = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-grace"},
    )
    manage_page = client.get(line_entry.json()["manage_url"], follow_redirects=True)
    assert manage_page.status_code == 200

    send_link = client.post("/captain/manage/send-email-verification")
    assert send_link.status_code == 200
    assert "Email 驗證連結" in send_link.text

    override = app.dependency_overrides[get_db]
    db_generator = override()
    db = next(db_generator)
    record = db.query(EmailVerification).filter(EmailVerification.team_id == team_id).first()
    verification_token = "test-token-grace-001"
    record.token_hash = hash_token(verification_token)
    db.add(record)
    db.commit()
    db.close()

    verify_page = client.get(f"/captain/verify-email?token={verification_token}")
    assert verify_page.status_code == 200
    assert "Email 驗證完成" in verify_page.text

    member_create = client.post(
        "/captain/manage/members",
        data={
            "name": "Henry",
            "phone": "0912000111",
            "is_alumni": "true",
        },
        follow_redirects=True,
    )
    assert member_create.status_code == 200
    assert "Henry" in member_create.text


def test_captain_logout_clears_web_session(client, admin_headers) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Logout Team",
            "captain_name": "Ivy",
            "captain_email": "ivy@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-ivy",
        },
        headers=admin_headers,
    )
    team_id = response.json()["id"]

    line_entry = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-ivy"},
    )
    manage_page = client.get(line_entry.json()["manage_url"], follow_redirects=True)
    assert manage_page.status_code == 200
    assert "Logout Team" in manage_page.text

    logout_response = client.post("/captain/logout", follow_redirects=True)
    assert logout_response.status_code == 200
    assert "XINDIAN_CUP" in logout_response.text

    denied_page = client.get("/captain/manage")
    assert "請先完成 LINE 驗證入口" in denied_page.text
