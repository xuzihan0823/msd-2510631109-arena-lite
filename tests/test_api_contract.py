import httpx
import pytest

from app.adapters.models import MockModelAdapter
from app.main import app, reset_for_tests


STUDENT_ID = "2510631109"
ALPHA = f"{STUDENT_ID}-model-alpha"
BETA = f"{STUDENT_ID}-model-beta"


async def login(client: httpx.AsyncClient, role: str) -> str:
    response = await client.post("/login", json={"role": role})
    assert response.status_code == 200
    return response.json()["token"]


async def create_ready_battle(client: httpx.AsyncClient, admin_token: str) -> str:
    response = await client.post(
        "/battles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"prompt": "Explain TDD in one sentence", "contestant_a_id": ALPHA, "contestant_b_id": BETA},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "answering"
    return response.json()["battle_id"]


@pytest.mark.anyio
async def test_login_rejects_unknown_role_and_protected_route_requires_matching_role() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert (await client.post("/login", json={"role": "other"})).status_code == 401
        assert (await client.post("/battles", json={})).status_code == 401
        voter_token = await login(client, "voter")
        response = await client.post(
            "/battles",
            headers={"Authorization": f"Bearer {voter_token}"},
            json={"prompt": "Explain TDD", "contestant_a_id": ALPHA, "contestant_b_id": BETA},
        )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_and_anonymous_view_follow_contract() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_token = await login(client, "admin")
        voter_token = await login(client, "voter")
        battle_id = await create_ready_battle(client, admin_token)
        response = await client.get(
            f"/battles/{battle_id}", headers={"Authorization": f"Bearer {voter_token}"}
        )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ready"
    assert body["answer_a"] and body["answer_b"]
    for forbidden in ("contestant_a_id", "contestant_b_id", "model_id", "name", "elo", "rank"):
        assert forbidden not in body


@pytest.mark.anyio
async def test_create_rejects_empty_prompt_self_battle_and_missing_battle() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_token = await login(client, "admin")
        headers = {"Authorization": f"Bearer {admin_token}"}
        empty = await client.post(
            "/battles", headers=headers, json={"prompt": "", "contestant_a_id": ALPHA, "contestant_b_id": BETA}
        )
        self_battle = await client.post(
            "/battles", headers=headers, json={"prompt": "TDD", "contestant_a_id": ALPHA, "contestant_b_id": ALPHA}
        )
        voter_token = await login(client, "voter")
        missing = await client.get(
            "/battles/2510631109-battle-missing", headers={"Authorization": f"Bearer {voter_token}"}
        )

    assert empty.status_code == 422
    assert self_battle.status_code == 422
    assert missing.status_code == 404


@pytest.mark.anyio
async def test_vote_settle_and_leaderboard_handle_main_and_error_paths() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_token = await login(client, "admin")
        voter_token = await login(client, "voter")
        battle_id = await create_ready_battle(client, admin_token)
        voter_headers = {"Authorization": f"Bearer {voter_token}"}
        first_vote = await client.post(f"/battles/{battle_id}/vote", headers=voter_headers, json={"choice": "A"})
        repeat_vote = await client.post(f"/battles/{battle_id}/vote", headers=voter_headers, json={"choice": "A"})
        wrong_role_settle = await client.post(f"/battles/{battle_id}/settle", headers=voter_headers)
        settled = await client.post(
            f"/battles/{battle_id}/settle", headers={"Authorization": f"Bearer {admin_token}"}
        )
        repeated_settle = await client.post(
            f"/battles/{battle_id}/settle", headers={"Authorization": f"Bearer {admin_token}"}
        )
        after_settle_vote = await client.post(f"/battles/{battle_id}/vote", headers=voter_headers, json={"choice": "B"})
        leaderboard = await client.get("/leaderboard", headers=voter_headers)

    assert first_vote.status_code == 200
    assert first_vote.json()["status"] == "voted"
    assert repeat_vote.status_code == 409
    assert wrong_role_settle.status_code == 401
    assert settled.status_code == 200
    assert settled.json()["status"] == "scored"
    assert set(settled.json()["elo_after"].values()) == {1484, 1516}
    assert repeated_settle.status_code == 409
    assert after_settle_vote.status_code == 409
    assert leaderboard.status_code == 200
    items = leaderboard.json()["items"]
    assert items == sorted(items, key=lambda item: (-item["elo"], item["model_id"]))


@pytest.mark.anyio
async def test_invalid_choice_and_settle_before_vote_are_rejected() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_token = await login(client, "admin")
        voter_token = await login(client, "voter")
        battle_id = await create_ready_battle(client, admin_token)
        premature_settle = await client.post(
            f"/battles/{battle_id}/settle", headers={"Authorization": f"Bearer {admin_token}"}
        )
        invalid_choice = await client.post(
            f"/battles/{battle_id}/vote",
            headers={"Authorization": f"Bearer {voter_token}"},
            json={"choice": "C"},
        )

    assert premature_settle.status_code == 409
    assert invalid_choice.status_code == 422


@pytest.mark.anyio
async def test_mock_timeout_aborts_battle_without_changing_elo() -> None:
    reset_for_tests()
    app.state.adapter = MockModelAdapter(failures={ALPHA: "timeout"})
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin_token = await login(client, "admin")
        voter_token = await login(client, "voter")
        response = await client.post(
            "/battles",
            headers={"Authorization": f"Bearer {admin_token}"},
           json={"prompt": "Explain TDD", "contestant_a_id": ALPHA, "contestant_b_id": BETA},
        )
        battle_id = response.json()["battle_id"]
        aborted = await client.get(
            f"/battles/{battle_id}", headers={"Authorization": f"Bearer {voter_token}"}
        )
        leaderboard = await client.get("/leaderboard", headers={"Authorization": f"Bearer {voter_token}"})

    assert response.status_code == 201
    assert aborted.status_code == 200
    assert aborted.json()["status"] == "aborted"
    assert aborted.json()["error_message"] == "timeout"
    assert all(item["elo"] == 1500 for item in leaderboard.json()["items"])