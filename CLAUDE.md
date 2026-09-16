# werk24-python

The public client library, published to PyPI as `werk24`. core-reader,
crew-api, crew-watchdog, werkflow and docs-v2 all install it straight from this
repository's main branch, so a breaking model change here lands in five other
repositories at once and has to go out with the matching migration.

## Getting the tests to run

```bash
uv venv .venv --python 3.13
uv pip install -r requirements.txt -r tests/requirements.txt -e .
.venv/bin/python -m pytest
```

337 passed, 4 skipped, about 45 seconds.

Three files, not one, and each does a different job:

- `pyproject.toml` holds the *flexible* constraints a consumer installing from
  PyPI resolves against.
- `requirements.txt` pins the exact versions that were tested together. It is
  what CI and local development install.
- `tests/requirements.txt` holds pytest, pytest-asyncio, PyYAML and hypothesis.
  Install it or the suite does not collect.

`-e .` installs the package itself. Without it `import werk24` picks up
whatever happens to be on the path, which in a mixed checkout is some other
repository's pinned release rather than the code you are editing.

## The four skipped tests

`tests/test_client.py` guards its live tests with a `requires_license` marker
that skips unless `W24TECHREAD_AUTH_TOKEN` and `W24TECHREAD_AUTH_REGION` are
set. Those four read a real drawing against the production API. CI supplies the
credentials from repository secrets; locally they skip, and that is the expected
result.

Everything else must run without credentials. If a test you are writing needs a
`Werk24Client`, construct it as `Werk24Client(token="t", region="r")` — a bare
`Werk24Client()` goes looking for a license and raises
`InvalidLicenseException` on any machine that has none. If the test enters the
client (`async with client:`), stub the socket too; `__aenter__` connects:

```python
with patch.multiple(
    client,
    _connect_with_retry=AsyncMock(),
    _graceful_shutdown=AsyncMock(),
):
    ...
```

`tests/test_ask_validation_integration.py` has the pattern.

## CI

`.github/workflows/python-test.yml` runs the suite on CPython 3.10 through
3.14 on every push. The floor is real: `pyproject.toml` declares
`requires-python = ">=3.10"` and carries version-marked pins (`pint` splits at
3.11), so a 3.10-only failure is a genuine break, not a CI quirk.
