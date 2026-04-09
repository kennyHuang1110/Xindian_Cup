"""Tests for the static LINE-gated site."""


def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_pages_redirect_to_line_login(client) -> None:
    for path in ["/", "/public/teams", "/history/photos", "/charter", "/schedule"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/line/login"


def test_line_login_page_renders(client) -> None:
    response = client.get("/line/login")
    assert response.status_code == 200
    assert "LINE 登入入口" in response.text


def test_line_login_allows_access_and_logout_clears_cookie(client) -> None:
    login_response = client.post(
        "/line/login",
        data={"line_user_id": "line-test-user"},
        follow_redirects=False,
    )
    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/"

    home_response = client.get("/", follow_redirects=True)
    assert home_response.status_code == 200
    assert "XINDIAN_CUP" in home_response.text

    logout_response = client.post("/line/logout", follow_redirects=False)
    assert logout_response.status_code == 303
    assert logout_response.headers["location"] == "/line/login"

    denied_response = client.get("/", follow_redirects=False)
    assert denied_response.status_code == 303


def test_public_teams_page_shows_static_team_roster(client) -> None:
    client.post("/line/login", data={"line_user_id": "line-test-user"}, follow_redirects=True)
    response = client.get("/public/teams")
    assert response.status_code == 200
    assert "新店校友 A 隊" in response.text
    assert "隊長：王小明" in response.text
    assert "陳小華" in response.text
    assert "是否為校友" in response.text


def test_schedule_page_renders_after_line_login(client) -> None:
    client.post("/line/login", data={"line_user_id": "line-test-user"}, follow_redirects=True)
    response = client.get("/schedule")
    assert response.status_code == 200
    assert "比賽循環圖與賽程表" in response.text
    assert "A 組" in response.text
    assert "09:00" in response.text
    assert "冠軍戰" in response.text


def test_history_and_charter_pages_render_after_line_login(client) -> None:
    client.post("/line/login", data={"line_user_id": "line-test-user"}, follow_redirects=True)

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
    assert payload[0]["team_name"] == "新店校友 A 隊"
    assert payload[0]["members"][0]["name"] == "王小明"


def test_line_entry_api_returns_access_url(client) -> None:
    response = client.post(
        "/api/auth/line-entry",
        json={"line_user_id": "line-test-user"},
    )
    assert response.status_code == 200
    assert response.json()["access_url"] == "/"
