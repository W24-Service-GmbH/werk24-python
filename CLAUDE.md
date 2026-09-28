# werk24-python
The public client library, published to PyPI as `werk24`. the server,
the API, the status monitor, the studio and the documentation site all install it straight from this
repository's main branch, so a breaking model change here lands in five other
repositories at once and has to go out with the matching migration.
## Getting the tests to run
```bash
uv venv .venv --python 3.13
uv pip install -r requirements.txt -r tests/requirements.txt -e .
.venv/bin/python -m pytest
```
391 passed, 5 skipped, about 75 seconds.
