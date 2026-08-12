import httpx
import pytest

from app.main import app, reset_for_tests


@pytest.mark.anyio
async def test_mock_backed_user_journey_reaches_scored_leaderboard() -> None:
    reset_for_tests()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        admin = (await client.post("/login", json={"role": "admin"})).json()["token"]
        voter = (await client.post("/login", json={"role": "voter"})).json()["token"]
        create = await client.post(
            "/battles",
            headers={"Authorization": f"Bearer {admin}"},
            json={
                "prompt": "Explain unit tests",
                "contestant_a": "2510631109-model-alpha",
                "contestant_b": "2510631109-model-beta",
            },
        )
        battle_id = create.json()["battle_id"]
        view = await client.get(f"/battles/{battle_id}", headers={"Authorization": f"Bearer {voter}"})
        vote = await client.post(
            f"/battles/{battle_id}/vote", headers={"Authorization": f"Bearer {voter}"}, json={"choice": "A"}
        )
        settle = await client.post(f"/battles/{battle_id}/settle", headers={"Authorization": f"Bearer {admin}"})
        leaderboard = await client.get("/leaderboard", headers={"Authorization": f"Bearer {voter}"})

    assert create.status_code == 201
    assert view.status_code == 200
    assert vote.status_code == 200
    assert settle.status_code == 200
    assert leaderboard.status_code == 200
