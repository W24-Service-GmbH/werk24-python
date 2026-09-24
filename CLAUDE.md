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

391 passed, 5 skipped, about 75 seconds.

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

## The skipped tests

`tests/test_client.py` guards its live tests with a `requires_license` marker
that skips unless `W24TECHREAD_AUTH_TOKEN` and `W24TECHREAD_AUTH_REGION` are
set. Those four read a real drawing against the production API. CI supplies the
credentials from repository secrets; locally they skip, and that is the expected
result.

The fifth is `tests/test_callback_e2e.py`, which needs `cloudflared` as well as
the credentials. See below.

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

## The callback check

A registered callback used to be unobserved end to end. The only test that
touched one submitted to `https://werk24.io` and asserted a request id came
back — and that URL is in core-reader's `SUPPRESSED_CALLBACKS`, so the server
returns before posting anything. Nothing had ever looked at a delivered
callback.

`tests/test_callback_e2e.py` closes that. It runs a receiver on loopback, puts
a Cloudflare quick tunnel in front of it for a public hostname, submits one
drawing against that hostname, and holds every callback that arrives against
the contract in `tests/callback_check/contract.py`: the transport headers, the
customer's own `callback_headers` coming back, each body parsing as a
`TechreadMessage`, the `STARTED` / `ASK` / `COMPLETED` sequence, and — the part
that matters most — `payload_dict` deserializing into a response model rather
than staying a plain dict, which is what a server/client drift looks like.

```bash
# needs cloudflared on PATH, or W24_CLOUDFLARED_BIN pointing at it
.venv/bin/python -m pytest -m callback_e2e -rs
```

It costs **one billable read per run**, so it is not part of the default suite
in CI: `python-test.yml` deselects it with `-m "not callback_e2e"` and
`callback-check.yml` runs it daily and on changes to the harness. It skips
locally when either the credentials or `cloudflared` are missing;
`W24_CALLBACK_CHECK_REQUIRED=1` turns that skip into a failure, which is what
CI sets so a missing secret cannot read as a green check.

The rules themselves are covered offline in `tests/test_callback_contract.py`
and `tests/test_callback_receiver.py` — 54 tests, no credentials, no network —
so a harness that has quietly stopped checking anything fails on an ordinary
push rather than on the next paid run.

## CI

`.github/workflows/python-test.yml` runs the suite on CPython 3.10 through
3.14 on every push. The floor is real: `pyproject.toml` declares
`requires-python = ">=3.10"` and carries version-marked pins (`pint` splits at
3.11), so a 3.10-only failure is a genuine break, not a CI quirk.

## Questions for the owner in every pull request

Every pull request body here ends with a section headed **Questions for the
owner**, even when all it says is "None". The owner decides from that section
without reading the diff, so a question buried in the middle of a description
is a question nobody answers. It is the same rule in every repository in the
group (core-reader#2436); the list on core-reader#2427
(https://github.com/W24-Service-GmbH/core-reader/pull/2427#issuecomment-5816887140)
is the one to match:

- **One opening line**: how many questions, and whether any blocks the merge.
- **Numbered questions, each in bold**, asked as yes/no or as a choice between
  named options.
- **One to three plain sentences under each**: what happens either way, with
  numbers where they exist.
- **`*Recommendation:*`** with the answer you would give.
- **Answerable without the diff.** Say what a customer or the owner would
  notice, not which function changed, and explain an internal name in one line
  the first time it appears.
- **Actions are not questions.** Things to do or watch after the deploy go in
  a short "Not questions, for after the deploy" list at the end.

When the owner asks "what do I need to decide?", answer in the same shape. When
a question is answered in the thread, write the answer into the body under it
(`*Answer:*`, with a link to the comment), so the body stays the record of what
was decided.

This repository is public, so the example is an illustration rather than a
real decision from another repository:

```markdown
## Questions for the owner

One question. It does not block the merge.

1. **Release this as 2.5.0 or as 3.0.0?**
   - It removes a field from `TechreadMessage`, so code that reads that field
     breaks on upgrade.
   - 3.0.0 says so to everyone installing from PyPI; 2.5.0 reaches every
     `werk24>=2` install without warning.
   - *Recommendation:* 3.0.0.
   - *Answer:* 3.0.0 (<link to the owner's comment>).

**Not questions, for after the deploy:**
- core-reader, crew-api, crew-watchdog, werkflow and docs-v2 install from main
  and pick this up on their next build.
```
