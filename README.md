# reproseed

Deterministic random contexts and stable fixture identifiers without monkey-patching the whole interpreter.

```bash
python -m pip install reproseed
```

```python
from reproseed import seeded

with seeded(2026) as run:
    print(run.rng.randint(1, 10))
    print(run.token("user-fixture"))
    print(run.uuid("order-fixture"))
```

`seeded()` temporarily seeds Python's module-level `random` generator and restores its previous state when the context exits. `SeededRun.rng`, `bytes()`, `uuid()`, and `token()` are explicit deterministic helpers for tests and local experiments.

The run also exposes deterministic `randint()`, `uniform()`, `choice()`, and `shuffle()` helpers, plus `fork(namespace)` for independently reproducible sub-runs.

The package deliberately does not fake wall-clock time, operating-system entropy, or network responses. Those boundaries should be controlled by the test framework or application dependency injection.
