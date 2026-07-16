import pytest

from app.storage.repository import ArenaStore, DuplicateVoteError


STUDENT_ID = "2510631109"
ALPHA = f"{STUDENT_ID}-model-alpha"
BETA = f"{STUDENT_ID}-model-beta"


def test_store_seeds_demo_contestants_at_1500() -> None:
    store = ArenaStore()

    assert store.get_contestant(ALPHA)["elo"] == 1500
    assert store.get_contestant(BETA)["elo"] == 1500


def test_store_enforces_one_vote_per_battle_and_voter() -> None:
    store = ArenaStore()
    battle_id = store.create_battle("Explain TDD", ALPHA, BETA, ALPHA, BETA)

    vote_id = store.add_vote(battle_id, f"{STUDENT_ID}-user-demo", "A")
    assert vote_id

    with pytest.raises(DuplicateVoteError):
        store.add_vote(battle_id, f"{STUDENT_ID}-user-demo", "A")
