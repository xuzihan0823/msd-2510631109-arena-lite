import random
from collections.abc import Sequence


class SameContestantError(ValueError):
    """Raised when a Battle would contain one contestant twice."""


def validate_distinct_contestants(contestant_a_id: str, contestant_b_id: str) -> None:
    if contestant_a_id == contestant_b_id:
        raise SameContestantError("a battle needs two distinct contestants")


def assign_slots(
    contestant_a_id: str,
    contestant_b_id: str,
    rng: random.Random | None = None,
) -> tuple[str, str]:
    validate_distinct_contestants(contestant_a_id, contestant_b_id)
    slots = [contestant_a_id, contestant_b_id]
    (rng or random.Random()).shuffle(slots)
    return slots[0], slots[1]
