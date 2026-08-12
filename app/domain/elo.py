from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


K_FACTOR = 32
MINIMUM_ELO = 100


@dataclass(frozen=True)
class EloUpdate:
    rating_a: int
    rating_b: int
    delta_a: int
    delta_b: int


def _round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _expected_rating(rating: int, opponent_rating: int) -> float:
    return 1 / (1 + 10 ** ((opponent_rating - rating) / 400))


def update_elo(rating_a: int, rating_b: int, *, winner: str) -> EloUpdate:
    """Apply the D10 zero-sum ELO rule to one settled A/B vote."""
    if winner not in {"A", "B"}:
        raise ValueError("winner must be A or B")

    winner_rating, loser_rating = (
        (rating_a, rating_b) if winner == "A" else (rating_b, rating_a)
    )
    theoretical_delta = _round_half_up(
        K_FACTOR * (1 - _expected_rating(winner_rating, loser_rating))
    )
    new_loser = max(MINIMUM_ELO, loser_rating - theoretical_delta)
    applied_delta = loser_rating - new_loser
    new_winner = winner_rating + applied_delta

    if winner == "A":
        return EloUpdate(
            rating_a=new_winner,
            rating_b=new_loser,
            delta_a=applied_delta,
            delta_b=-applied_delta,
        )
    return EloUpdate(
        rating_a=new_loser,
        rating_b=new_winner,
        delta_a=-applied_delta,
        delta_b=applied_delta,
    )
