"""Basic smoke tests for the MVP application."""

def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Xindian_Cup Running" in response.text


def test_admin_create_team_sets_pending_status(client) -> None:
    response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Riverside Shooters",
            "captain_name": "Alice",
            "captain_email": "alice@example.com",
            "captain_phone": "0912345678",
            "captain_line_user_id": "line-alice",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["team_name"] == "Riverside Shooters"
    assert payload["status"] == "pending"


def test_public_teams_page_shows_active_team_and_members(client) -> None:
    team_response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Active Team",
            "captain_name": "Bob",
            "captain_email": "bob@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-bob",
        },
    )
    team_id = team_response.json()["id"]

    verification_response = client.post(
        "/api/captain/send-email-verification",
        json={"team_id": team_id, "email": "bob@example.com"},
    )
    assert verification_response.status_code == 200
    verification_token = verification_response.json()["verification_token"]

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

    verify_response = client.get(f"/api/captain/verify-email?token={verification_token}")
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "verified"

    line_entry_response = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-bob"},
    )
    assert line_entry_response.status_code == 200
    session_token = line_entry_response.json()["session_token"]
    headers = {"Authorization": f"Bearer {session_token}"}

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


def test_line_entry_rejects_mismatched_line_user(client) -> None:
    team_response = client.post(
        "/api/admin/teams",
        json={
            "team_name": "Mismatch Team",
            "captain_name": "Dana",
            "captain_email": "dana@example.com",
            "captain_phone": None,
            "captain_line_user_id": "line-dana",
        },
    )
    team_id = team_response.json()["id"]

    verification_response = client.post(
        "/api/captain/send-email-verification",
        json={"team_id": team_id, "email": "dana@example.com"},
    )
    verification_token = verification_response.json()["verification_token"]
    client.get(f"/api/captain/verify-email?token={verification_token}")

    line_entry_response = client.post(
        "/api/auth/line-entry",
        json={"team_id": team_id, "line_user_id": "line-someone-else"},
    )
    assert line_entry_response.status_code == 403
