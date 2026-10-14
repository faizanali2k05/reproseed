from __future__ import annotations

import hashlib
import random
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import MutableSequence, Sequence, TypeVar, Iterator


T = TypeVar("T")


@dataclass(frozen=True)
class SeededRun:
    """A run-local random generator and namespace-stable token source."""

    seed: int
    rng: random.Random

    def randint(self, a: int, b: int) -> int:
        """Return a deterministic integer in the inclusive range ``[a, b]``."""

        return self.rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        """Return a deterministic floating-point sample in ``[a, b]``."""

        return self.rng.uniform(a, b)

    def choice(self, values: Sequence[T]) -> T:
        """Choose one item from a non-empty sequence deterministically."""

        return self.rng.choice(values)

    def shuffle(self, values: MutableSequence[T]) -> None:
        """Shuffle a mutable sequence in place using this run's generator."""

        self.rng.shuffle(values)

    def token(self, namespace: str = "default") -> str:
        return stable_token(self.seed, namespace)

    def bytes(self, namespace: str = "default", length: int = 16) -> bytes:
        """Return deterministic bytes derived from the seed and namespace."""

        if length < 0:
            raise ValueError("length must be non-negative")
        output = bytearray()
        counter = 0
        while len(output) < length:
            payload = f"{self.seed}:{namespace}:{counter}".encode("utf-8")
            output.extend(hashlib.sha256(payload).digest())
            counter += 1
        return bytes(output[:length])

    def uuid(self, namespace: str = "default") -> uuid.UUID:
        """Return a deterministic UUID suitable for fixtures and test data."""

        return uuid.UUID(bytes=self.bytes(namespace, 16))

    def fork(self, namespace: str) -> "SeededRun":
        """Create an independent deterministic run derived from this run."""

        derived = int.from_bytes(self.bytes(namespace, 8), "big")
        return SeededRun(seed=derived, rng=random.Random(derived))


def stable_token(seed: int, namespace: str = "default") -> str:
    payload = f"{seed}:{namespace}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


@contextmanager
def seeded(seed: int) -> Iterator[SeededRun]:
    """Temporarily seed the module-level PRNG and restore its previous state.

    Prefer the run-local helpers for application code. The global generator is
    changed only for the duration of this context, which is convenient for
    legacy code and tests that already use :mod:`random` directly.
    """

    previous = random.getstate()
    random.seed(seed)
    try:
        yield SeededRun(seed=seed, rng=random.Random(seed))
    finally:
        random.setstate(previous)
