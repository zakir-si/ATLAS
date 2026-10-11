# Tests and expected behaviour

Run locally:

~~~bash
python -m pip install -e '.[dev]'
pytest -q
ruff check .
mypy src
~~~

Tests cover selector eligibility, invalid measurements, budget enforcement, health routes, UI serving and API validation. CI runs on pushes to main and pull requests targeting main.

No test output is checked in as proof of passing. Actual CI status is the source of truth after the workflow executes. Example data is synthetic and must not be presented as measured training performance.
