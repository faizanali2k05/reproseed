import random

import pytest

from reproseed import seeded, stable_token


def test_seeded_restores_global_random_state() -> None:
    random.seed(11)
    previous = random.getstate()
    with seeded(7) as run:
        assert run.rng.random() == random.Random(7).random()
        assert run.token("fixture") == stable_token(7, "fixture")
    assert random.getstate() == previous


def test_seeded_bytes_and_uuid_are_stable() -> None:
    with seeded(42) as first, seeded(42) as second:
        assert first.bytes("x", 40) == second.bytes("x", 40)
        assert first.uuid("x") == second.uuid("x")


def test_bytes_rejects_negative_length() -> None:
    with seeded(1) as run:
        with pytest.raises(ValueError):
            run.bytes(length=-1)


def test_local_helpers_and_forks_are_repeatable() -> None:
    with seeded(9) as first, seeded(9) as second:
        assert [first.randint(1, 100), first.choice(("a", "b"))] == [
            second.randint(1, 100),
            second.choice(("a", "b")),
        ]
        assert first.fork("worker").token() == second.fork("worker").token()
