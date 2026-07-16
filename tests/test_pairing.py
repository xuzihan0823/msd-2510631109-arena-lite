import random

import pytest

from app.domain.pairing import SameContestantError, assign_slots, validate_distinct_contestants


def test_same_contestant_is_rejected() -> None:
    with pytest.raises(SameContestantError):
        validate_distinct_contestants("2510631109-model-alpha", "2510631109-model-alpha")


def test_slot_assignment_keeps_both_contestants_and_can_change_order() -> None:
    first = assign_slots("2510631109-model-alpha", "2510631109-model-beta", random.Random(1))
    second = assign_slots("2510631109-model-alpha", "2510631109-model-beta", random.Random(0))

    assert set(first) == {"2510631109-model-alpha", "2510631109-model-beta"}
    assert set(second) == {"2510631109-model-alpha", "2510631109-model-beta"}
    assert first != second
