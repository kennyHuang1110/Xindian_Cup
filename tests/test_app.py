"""Tests for the public static site."""


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_are_present(client) -> None:
    response = client.get("/")
    assert response.headers["Content-Security-Policy"].startswith("default-src 'self'")
    assert response.headers["Permissions-Policy"]
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "0"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert response.headers["Cross-Origin-Embedder-Policy"] == "unsafe-none"
    assert "Strict-Transport-Security" not in response.headers


def test_public_pages_render(client) -> None:
    for path in ["/", "/public/teams", "/history/photos", "/charter", "/schedule"]:
        response = client.get(path)
        assert response.status_code == 200


def test_index_page_renders(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "XINDIAN_CUP" in response.text
    assert "查看賽程表" in response.text
    assert "報名表" not in response.text


def test_public_teams_page_shows_team_captain_and_members_only(client) -> None:
    response = client.get("/public/teams")
    assert response.status_code == 200
    assert "傻眼圈圈" in response.text
    assert "隊長：祁櫂笎" in response.text
    assert "石佳興" in response.text
    assert "是否為校友" not in response.text


def test_schedule_page_renders(client) -> None:
    response = client.get("/schedule")
    assert response.status_code == 200
    assert "比賽循環圖與賽程表" in response.text
    assert "A 組" in response.text
    assert "09:00" in response.text
    assert "W3 vs W4" in response.text
    assert "T3A" in response.text


def test_history_and_charter_pages_render(client) -> None:
    history_response = client.get("/history/photos")
    assert history_response.status_code == 200
    assert "歷屆照片" in history_response.text
    assert "2024" in history_response.text

    charter_response = client.get("/charter")
    assert charter_response.status_code == 200
    assert "2026 新店盃混排校友賽" in charter_response.text
    assert "壹、主旨" in charter_response.text


def test_public_api_returns_static_team_data(client) -> None:
    response = client.get("/api/public/teams")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["team_name"] == "1"
    assert payload[0]["members"][0]["name"] == "馮卓弋"
