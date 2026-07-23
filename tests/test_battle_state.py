import pytest

from app.domain.battle import IllegalStateTransition, transition


def test_happy_path_transitions_are_allowed() -> None:
    assert transition("created", "answering") == "answering"
    assert transition("answering", "ready") == "ready"
    assert transition("ready", "voted") == "voted"
    assert transition("voted", "scored") == "scored"


def test_adapter_failure_moves_answering_battle_to_aborted() -> None:
    assert transition("answering", "aborted") == "aborted"


@pytest.mark.parametrize(
    ("current", "target"),
    [("ready", "scored"), ("scored", "voted"), ("aborted", "voted")],
)
def test_illegal_transition_is_rejected(current: str, target: str) -> None:
    with pytest.raises(IllegalStateTransition):
        transition(current, target)
