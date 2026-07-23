from app.domain.elo import update_elo


def test_equal_ratings_a_win_updates_by_sixteen() -> None:
    result = update_elo(1500, 1500, winner="A")

    assert result.rating_a == 1516
    assert result.rating_b == 1484
    assert result.delta_a == 16
    assert result.delta_b == -16
    assert result.delta_a + result.delta_b == 0


def test_equal_ratings_b_win_is_symmetric() -> None:
    result = update_elo(1500, 1500, winner="B")

    assert result.rating_a == 1484
    assert result.rating_b == 1516
    assert result.delta_a + result.delta_b == 0


def test_loser_rating_never_falls_below_minimum_and_update_stays_zero_sum() -> None:
    result = update_elo(100, 101, winner="A")

    assert result.rating_b == 100
    assert result.rating_a == 101
    assert result.delta_a + result.delta_b == 0
