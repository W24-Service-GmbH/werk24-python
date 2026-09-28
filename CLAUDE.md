# core-reader

The production read path. Every customer request for a drawing runs through this
code. `REVIEW.md` says what a review flags; `.claude/skills/steward/SKILL.md`
says how a pull request here gets to a mergeable state;
`.claude/skills/monitoring/SKILL.md` says how to read what production is doing
and which of its instruments can be trusted;
`.claude/skills/llm-budget-review/SKILL.md` is the monthly review of the LLM
hedge and of how often a prompt still runs out of time (the fixed per-prompt
budgets, which expired quietly into an empty result, were replaced on
2026-09-23 by waiting as long as the request can use the answer); `docs/LOGGING.md` says what a log line here
has to look like, and why Sentry's wiring makes that more than a style
question. This file says how to get the tests running and how to tell whether a
merge to `prod` actually reached production, because those are the parts that
were being rediscovered from scratch every time.

## Filing an issue

Every issue opened here, by hand or by a skill (`monitoring`,
`grammar-gap-review` and the perf reviews all file them), is created with all
three of these set. An issue missing one is not triaged, and the backlog
cannot be sorted.

- **Priority**, the org issue field (`Urgent` / `High` / `Medium` / `Low`):
  - `Urgent`: customers are affected in production now (a stall, failed
    requests, an SLA the watchdog sees).
  - `High`: a measured KPI, read-rate or cost regression, or a lever with a
    large measured payoff. Fix this cycle.
  - `Medium`: a known improvement with a clear, measured payoff.
  - `Low`: small or unmeasured payoff, speculative, or nice to have.

  Judge by measured impact, not by how interesting the fix is. Keep the
  number of open `Urgent` and `High` issues small, or the field stops meaning
  anything.
- **Effort**, the org issue field (`High` / `Medium` / `Low`): `Low` is a
  flag flip or a one-file change, `Medium` is a few files or a single
  cross-cutting change, `High` is multi-day, cross-repo or needs a design.
- **At least one label.** Reuse an existing one (`performance` for speed and
  cost work); create a new label only when none fits, and say so in the
  issue.

With the GitHub MCP tools, set the fields on the same `issue_write` call that
creates the issue:
`issue_fields: [{"field_name": "Priority", "field_option_name": "High"},
{"field_name": "Effort", "field_option_name": "Low"}]` plus `labels`. Put one
sentence in the body saying why the priority is what it is, so the next
re-triage can check it.

## Public repositories: write nothing there, except a release the owner asks for

**werk24-python is public.** Everything a session here reads is internal:
Sentry numbers, customer and account names, request volumes, costs, prompts,
infrastructure, and the contents of this repository. So from a core-reader
session, nothing is written to werk24-python: no issue, no comment, no review,
no pull request, no push. Reading it (code search, `git ls-remote`, installing
it) is fine.

A finding whose fix lives in werk24-python is filed **here**, labelled
`werk24-python`, with one line saying the fix belongs there. A person decides
what, if anything, goes public, and writes it for a public reader.

### The one exception: cutting a release

When the owner asks for a werk24-python release in so many words ("make a
werk24-python release", "release werk24 2.8.0"), a session here may do exactly
these writes to werk24-python, and nothing else:

1. A branch named `release/<version>` and one pull request from it that changes
   only the version (`pyproject.toml`, and the changelog if the repository
   keeps one). Nothing else rides along: no fix, no dependency bump, no docs.
2. After that pull request is merged, the tag `<version>` on the merge commit.
   The GitHub MCP tools a session has here can read releases but not create
   one, and there is no `gh`, so the session drafts the release text and the
   owner publishes the release from it (or a workflow in werk24-python does,
   on the tag).

What may be written in any of them is limited to what werk24-python already
says in public about itself:

- **The release notes are built from werk24-python's own history**: the commit
  subjects and merged pull request titles between the previous tag and the new
  one, rewritten for a client user where needed. Nothing else is a source.
- **Never** mention core-reader, crew-api, infrastructure, Sentry, a metric, a
  customer, an account, a username, a volume, a cost, a prompt, a model or an
  internal issue or pull request number, even to explain why a change was
  made. "Why" is exactly where internal context leaks; a release note says
  *what* changed for someone calling the client.
- **The version** follows semver from those commits: a patch for fixes only, a
  minor for any new field, exception, CLI flag or behaviour, a major for
  anything a caller has to change. When core-reader gates behaviour on a
  client version (as `READ_INCOMPLETE_WARNING_ENABLED` does on 2.8.0), check
  that the release actually contains the change it waits for, and ask the
  owner rather than bumping the number to fit.
- **Show the owner the version and the full release text before tagging**, in
  the chat, and tag only on their go-ahead. A tag and a release on a public
  repository are published the moment they exist, and a published version on
  PyPI cannot be reused even if it is yanked.

Anything outside those two steps, an issue, a comment, a review, a fix pushed
alongside the bump, stays forbidden from here, however small.

### What enforces it

`.claude/hooks/public_repo_guard.py`, wired as a `PreToolUse` hook in
`.claude/settings.json`, refuses any GitHub MCP write whose `owner/repo` is on
its `PUBLIC_REPOS` list, and any shell push, `gh` write or `api.github.com`
call that names one (or runs inside a clone of one). Add a repository to that
list the day it goes public.

The release exception is carved out in the same file, as narrowly as the rule
above: on a public repository it lets through only `create_branch` and
`create_or_update_file` / `push_files` on a `release/*` branch,
`create_pull_request` from a `release/*` head, and a shell push of a
`release/*` branch or of a tag matching `^\d+\.\d+\.\d+$`. Every other write,
`issue_write`, `add_issue_comment`, a review, `merge_pull_request` and a push
to any other branch included, is still refused. The owner merges the release
pull request; the session does not.
`tests/build/test_public_repo_guard.py` pins both the refusals and the
exception; widening the exception means changing that test on purpose.

A session also needs werk24-python attached with push access (`add_repo`
with `access: "push"`); this repository's session scope does not include it
by default.

A known gap: the hook only runs in sessions opened on this repository. A
session opened on werk24-python itself is not guarded by it, so do not carry
core-reader findings into one.

## Questions for the owner in every pull request

Every pull request body here ends with a section headed **Questions for the
owner**, even when all it says is "None". The owner decides from that section
without reading the diff, so a question buried in the middle of a description
is a question nobody answers. The list on #2427
(https://github.com/W24-Service-GmbH/core-reader/pull/2427#issuecomment-5816887140)
is the one the owner asked every pull request to match. Its shape:

- **One opening line**: how many questions, and whether any blocks the merge.
- **Numbered questions, each in bold**, asked as yes/no or as a choice between
  named options. "Thoughts?" is not a question.
- **One to three plain sentences under each**: what happens either way, with
  numbers where they exist.
- **`*Recommendation:*`** with the answer you would give.
- **Answerable without the diff.** Say what a customer or the owner would
  notice, not which function changed, and explain an internal name (a flag, a
  metric, a format) in one line the first time it appears.
- **Actions are not questions.** Things to do or watch after the deploy go in
  a short "Not questions, for after the deploy" list at the end.

Two rules keep it true after the pull request is opened. When the owner asks
"what do I need to decide?", answer in this same shape. And when a question is
answered in the thread, write the answer into the body under its question
(`*Answer:*`, with a link to the comment), so the body stays the record of what
was decided and nobody has to rebuild it from the conversation.

Trimmed from #2427:

```markdown
## Questions for the owner

Three questions. None blocks the merge; each has a recommendation.

1. **Is it fine that three customer formats start filling fields that were always empty?**
   - dimanex, swiss_topics and ceramtec_standard_v1 have shipped the drawing
     number, material and general tolerances empty, because they read the
     title block from a path that no longer exists. After this PR they fill them.
   - A customer whose system expects those fields empty will suddenly see values.
   - *Recommendation:* yes, it is a fix. Tell the customers who use these formats.

2. **Turn on the page-OCR fallback for unread labels (`LABEL_PAGE_OCR_FALLBACK`)?**
   - It fills a label Textract could not read from the page's own OCR. It is off.
   - Switching it on wants a check of about 100 unread label crops first.
   - *Recommendation:* keep it off until that check is done.

3. **Add a Sentry alert when pages fail inside a read?**
   - This PR starts counting failed pages. An alert per release would catch a
     release that breaks pages.
   - *Recommendation:* yes.
   - *Answer:* yes (https://github.com/W24-Service-GmbH/core-reader/pull/2427#issuecomment-5817008111).

**Not questions, for after the deploy:**
- Watch memory on multi-page A0 reads (`request.memory.peak_ratio`); revert
  #2378 if it gets close to 1.
```

## Getting the tests to run

```bash
uv venv .venv --python 3.14
uv pip install -r requirements.txt -r requirements-dev.txt
export AWS_DEFAULT_REGION=eu-central-1
.venv/bin/python -m pytest -m "not quality"
```

Four things in there are not guessable, and each one cost a session to find:

**Python 3.14, not the interpreter on `PATH`.** `numpy==2.5.3` declares
`Python>=3.12`, so `requirements.txt` does not even *resolve* on 3.11 — the
error is a resolver message about numpy, which reads like a bad pin rather than
a wrong interpreter. `Dockerfile.base` builds on `python:3.14-slim`; match it.

3.14 is new here as of 2026-09-21 and 3.13 still resolves, installs and runs
the suite, so a venv that is quietly on the old interpreter does not announce
itself. Two things make that worth checking rather than assuming:

**And before concluding the interpreter is wrong, check which 3.14 `uv`
actually handed you.** In an agent sandbox on 2026-09-21,
`uv venv .venv --python 3.14` resolved to **3.14.0rc2** -- the newest 3.14 in
that machine's `uv python list`, with no 3.14.7 offered for download -- and
pydantic does not work on it. The suite dies during collection with
`TypeError: _eval_type() got an unexpected keyword argument
'prefer_fwd_module'`, which names neither pydantic nor the interpreter and
reads like a broken pin. `uv python list` settles it in thirty seconds; if
3.14.7 is not there, build the venv on 3.13 and say so in the pull request
rather than measuring against a release candidate. The identical-id evidence
below is evidence about 3.14.7, not about an rc, which is what makes that
substitution honest.

- **Nothing in the pin set moved for 3.14.** Every version in
  `requirements.txt` and `requirements-dev.txt` installs unchanged on 3.14.7,
  and two venvs built from them resolve to byte-identical package lists, so a
  difference between two runs is the interpreter and nothing else.

  What needed a second look was the wheels whose filenames name an older
  CPython and install on 3.14 anyway, because they are `abi3`: OpenCV
  (`cp37-abi3`) and tokenizers (`cp310-abi3`). **There are two OpenCV
  pins, and they are now the same version.** `Dockerfile.base` installs
  `opencv-contrib-python-headless` into `/opt/py314` and
  `requirements-dev.txt` pins it for a local environment; both are
  `5.0.0.93` since #2430, and `tests/build/test_opencv_pins.py` fails when
  they drift apart. Until then the image ran 4.11.0.86, whose bundled
  libtiff 4.6.0 lacked the 4.7.x fixes, against 5.0.0.93 locally. **The
  image only gets the new version when the base is rebuilt** with
  `utils/build_new_base.sh` and an app image is built on it, the same as
  every other base change.

  What 4.11.0.86 against 5.0.0.93 changes, measured on 2026-09-24 on
  3.14.7: the 93 test files that touch OpenCV give identical failing ids
  on both, bar the libtiff check that fails on 4.11 by design. Decoding is
  identical: 119 files (seven customer TIFFs from the Weidmann strip
  corpus, 12 synthetic TIFFs across LZW, deflate, packbits, raw, JPEG, G3,
  G4 and 16-bit, and the repository's JPEGs and PNGs) give
  byte-identical arrays through `imread` and `imdecode`, and the
  `INTER_AREA`, `INTER_LINEAR` and `INTER_LANCZOS4` resizes, 90 and 180
  degree rotations, thresholds, contours and morphology match on those
  plus 20 rendered Weidmann pages.

  **`cv2.minAreaRect` changed convention in 4.13**: 4.11 reported the angle
  in `(0, 90]`, 4.13 and 5.x in `[-90, 0)` with width and height swapped,
  and `cv2.boxPoints` moves two corners by a unit in the last place. Raw,
  that made `Rectangle.angle` of an axis-aligned contour -90 instead of 0,
  and `lib/annotator/utils.py` rotates `auto_rotate` label crops by it.
  `crew/image/rectangle/rectangle.py` pins both to 4.11's answer
  (`min_area_rect`, `box_points`), and `Contour.min_area_rect` and
  `Rectangle.contour` go through them. Over 118,680 contours from those
  images, on 5.0.0.93: `Rectangle.angle` matches 4.11 on all of them (raw:
  2,510), the whole triple on 101,990, and `Contour.rangle` on all but 276
  exact squares; the other 16,690 are axis-aligned boxes 4.11 itself
  reported as `(h, w, 0)` rather than `(w, h, 90)`, depending on which tied
  caliper it met last, and they get the same box with width and height the
  other way round. On 4.11 the helpers return exactly what `cv2` does.
  Anything that reads the angle, or which side is the width, should call
  `min_area_rect` rather than `cv2.minAreaRect`; `Image`'s content-bounds
  `area()` calls `cv2` directly and reads only `w * h`, which both agree on.

  Three things still differ, and no unit test notices: `warpAffine` at a
  small angle (`Image.rotate`) differs on about 4% of pixels by up to 6
  grey levels; `cv2.approxPolyDP` returns a different polygon for 82 of
  47,957 contours at the `0.04 * perimeter` epsilon the indicator-region
  code uses; and `cv2.calcHist` returns shape `(256,)` rather than
  `(256, 1)`, which `Image` flattens anyway. So `pytest -m quality` before
  the base rebuild is what says whether reads moved.
- **The differences that do exist are speed.** `copy.deepcopy` is roughly
  three times faster (it is C from 3.14 on), which was enough to break one
  test outright -- see the entry under "Known-red tests". Any other test whose
  setup does a fixed amount of pure-Python work and then asserts on a clock is
  the same hazard waiting to happen; make the work deadline-driven rather than
  count-driven when you meet one.

`mp.get_context("spawn")` in `lib/jargon/reader/parallel_parser.py` was already
explicit, so 3.14's change of the default start method on Linux (`fork` to
`forkserver`) does not reach the parse pool. Do not drop that argument.

**Merging the 3.14 change does not put 3.14 into production.** `Dockerfile`
builds `FROM werk24/core-reader-base:latest`, and nothing rebuilds the base
image automatically -- the same property the embedding-model section below is
about. Until someone runs `utils/build_new_base.sh` and an app image is built
on the result, every app build still lands on the old base and production
keeps serving the old interpreter, with no error anywhere to say so. That is a
quiet state rather than a broken one: the app image builds and runs fine, it
is just not the interpreter this file claims.
`/opt/py314/bin/python3.14 --version` early in `Dockerfile` prints what the
base actually carries, which is the cheapest place to catch it.

### There are now two interpreters, and two Dockerfiles

This got more involved on 2026-09-21 when the app image went distroless, so
it is worth laying out rather than inferring:

| File | What it builds | Interpreter |
| --- | --- | --- |
| `Dockerfile.base` | `werk24/core-reader-base`, the build substrate | Debian's `python:3.14-slim` **and** a relocatable 3.14 at `/opt/py314` |
| `Dockerfile` | the app image that runs | distroless, `/opt/py314` only |

`Dockerfile.debian`, the Debian app image kept as a fallback while the
distroless one was new, and `Dockerfile.base.chainguard`, an A/B variant of
the base that was never adopted, were both deleted on 2026-09-24 (#2430).
CodeBuild builds `Dockerfile` (the core-reader2 buildspec passes no `-f`).

`Dockerfile.base` cannot itself be distroless and never will be: it apt-gets,
it compiles CBC from source with coinbrew, and the app image pip-installs on
top of it. What it does now is carry a **second** interpreter at `/opt/py314`,
fetched by `uv`, and that is the one the app image builds wheels against and
ships.

The reason is ABI, and it is not a preference. `python:3.14-slim`'s
`/usr/local/bin/python` dynamically links Debian's libssl, libcrypto,
libexpat, libffi, libsqlite3, libreadline and libncurses, so it cannot enter a
distroless stage without all of them; the python-build-standalone build links
only glibc core with OpenSSL statically in. And 54 of the extension modules in
`requirements.txt` are cp314-locked against only 6 abi3, so **the interpreter
that builds the wheels must be the one that runs them**. Mixing the two gives
you `ImportError` on numpy at container start, not at build.

`Dockerfile.base` therefore installs OpenCV and pulp into `/opt/py314`,
because "the base image carries them" (the note under `requirements.txt`
below) has to hold for the interpreter the app image ships. That is the only
place the base installs them. Until #2430 it installed both into the Debian
python as well, for `Dockerfile.debian`; with that image gone nothing reads
the Debian python's site-packages, so it carries neither.

**Every install into `/opt/py314` needs `--break-system-packages`.**
`uv python install` drops a PEP 668 marker in the interpreter it fetches
(`/opt/py314/lib/python3.14/EXTERNALLY-MANAGED`, "This Python installation is
managed by uv and should not be modified"), and both installers honour it:
pip refuses with `error: externally-managed-environment`, uv with `error: The
interpreter at /opt/py314 is externally managed`. So switching installer is
not a way around it, and neither file deletes the marker -- `Dockerfile.base`
passes the flag for OpenCV and pulp, `Dockerfile` passes it for
`requirements.txt`. The marker is meant for an interpreter uv resolves for
you; `/opt/py314` is the opposite, the thing packages are deliberately put
into. A venv is not the alternative, because the runtime stage copies
`/opt/py314` wholesale and runs it by absolute path.

`Dockerfile` installs `requirements.txt` with **uv**, not pip. uv ships in the
base image at `/usr/local/bin/uv` (`Dockerfile.base` copies it from the pinned
`ghcr.io/astral-sh/uv:0.12.17`), so the app build adds no tooling for it, and
the early version check in `Dockerfile` covers `uv` alongside the interpreter
for the same reason: to catch a base image older than what the file assumes.
`Dockerfile.base` still uses pip for its own two packages.

**A local `docker build` needs `WERK24_SHA`.** werk24 installs from
werk24-python's main branch, unpinned on purpose, and `Dockerfile` installs it
once, after the hashed lock, in a layer of its own keyed on `ARG WERK24_SHA`,
so the build's registry cache (infrastructure#228) never freezes it. An empty value is a cache key
too, so a rebuild without the argument reuses the werk24 of the first build.
The builder stage therefore refuses a build that passes neither `WERK24_SHA`
nor `W24_RELEASE`: pass
`--build-arg WERK24_SHA=$(git ls-remote https://github.com/W24-Service-GmbH/werk24-python.git refs/heads/main | cut -f1)`
(the README has the whole command), or `WERK24_SHA=unpinned` to accept a
stale werk24 knowingly. A release build is exempt because every CodeBuild
path that omits the SHA starts from an empty layer cache.

**The distroless image depends on a health check in another repository, and
merged is not applied.** The ECS check used to be
`["CMD-SHELL", "curl -f http://localhost/ || exit 1"]`
(`infrastructure/modules/services/core-reader2/ecs.tf`). There is no shell and
no curl in a distroless image, so every task would fail its check and ECS
would kill it in a loop.

infrastructure#197 replaced it with a `CMD` form driving `python` from `PATH`
-- which resolved on the Debian image then running *and* on the distroless
one, so it was safe to deploy ahead of any image change -- and that PR is
**merged**. It is not necessarily **applied**: merging terraform runs no
`apply`, the same way merging here builds no image. Confirm the live task
definition carries the new command before pointing CodeBuild at `Dockerfile`.

It uses `127.0.0.1`, not `localhost`, and that is deliberate: the distroless
base ships no `/etc/hosts` and no `/etc/resolv.conf`. Runtimes bind-mount both
at container start so the name does resolve in a real task, but the literal
address costs no resolver round trip and cannot fail closed. Measured in a
rootfs built from the real distroless layers: the `localhost` form raises
`socket.gaierror: Temporary failure in name resolution`; the address returns 0.

### The first deploy of the distroless image, and what the build checks now

The first CodeBuild build of `Dockerfile` ran on 2026-09-22 (prod at
`dee486bd`). It succeeded, the image deployed, Sentry initialised on the new
release, and three minutes later every parse worker died in its initializer:

```
OSError: [Errno 30] Read-only file system:
  '/app/lib/jargon/reader/assets/compiled/.callout_master.pgc.ni7k_3yb'
```

Two facts combined, and neither is visible in a build log. parglare writes a
parse table through `NamedTemporaryFile`, so `callout_master.pgc` and
`cell_master.pgc` came out of `lib.jargon.compile` with mode **0600, owned by
root** (the builder stage runs as root). The runtime stage runs as uid 65532
on a read-only root, so each worker could not read the table, recomputed it
(tens of seconds), and then died writing it back -- parglare catches
`PermissionError` on that write, not `EROFS`. The Debian app image before it
never hit this because it compiled and ran as the same user on a writable
filesystem.

Three things changed, and the last is the one to keep in mind when editing
the Dockerfile:

- `lib/jargon/compiler/grammar.py::publish_parse_table` chmods the table to
  0644 after building it. The producer of the artefact owns its mode.
- `lib/jargon/reader/build.py::compile_grammar_reader` loads with
  `force_load_table` and, if that fails, recomputes **in memory** with
  `table_cache=False` and logs at ERROR. The runtime never writes a table.
- **The runtime stage ends with `RUN [..., "-m", "lib.jargon.verify"]`, after
  `USER 65532:65532`.** It walks the compiled tree and the embedding model
  checking mode bits against that uid, loads both tables with `force_load`,
  unpickles the readers and asks libmagic to classify a PDF header. It writes
  nothing and refuses to run as root, because root reads every file and the
  check would prove nothing. `tests/build/test_runtime_stage.py` pins the
  ordering. To run it on a dev machine the way the image does:

  ```bash
  setpriv --reuid=65532 --regid=65532 --clear-groups \
    env AWS_DEFAULT_REGION=eu-central-1 EMBEDDING_MODEL_DIR=<dir> HOME=/tmp \
    .venv/bin/python -m lib.jargon.verify
  ```

  As root without dropping privileges it exits 2; `--allow-root` runs the
  load checks alone.

The same deploy also printed, twice per process,
`/etc/magic, 0: Warning: using regular magic file '/usr/share/misc/magic'`.
The runtime stage copies `/usr/lib/file/magic.mgc` but not Debian's symlinks
to it, and libmagic's compiled-in search path only knows the symlink names.
`ENV MAGIC=/usr/lib/file/magic.mgc` names the file directly; the
verification step loads through it.

**`requirements.txt` is not the dependency list.** It is the list pip installs
*inside the image*, on top of `werk24/core-reader-base`. Everything the base
image already carries is missing from it: OpenCV and pulp (with the CBC
binary). `requirements-dev.txt` holds that set plus the test runners, and
explains each entry. Without it the first import of `settings/` fails on `cv2`
and nothing in the repository loads.

**And the image does not install `requirements.txt` at all.** It installs
`requirements.lock` with `--require-hashes` (#2400): every package the pins
resolve to, at an exact version with the sha256 of every file PyPI
publishes for it. So a pin changed in `requirements.txt` reaches production
only once `sh tools/lock_requirements.sh` has been run and the lock committed
with it; `tests/build/test_requirements_lock.py` fails until then, when it
is run: pytest's default `norecursedirs` skips any directory named `build`,
so a run from the repository root, `.github/workflows/unit.yml` included,
never collects `tests/build/` (run `pytest tests/build` by name). werk24 is
the exception: it stays on werk24-python main, installs on its own with
`--no-deps`, and `uv pip check` fails the image build when main has asked
for a dependency the lock does not carry. The build writes a `pip freeze`,
werk24's commit included, to `/app/build-info/pip-freeze.txt` and prints it
in the build log. A local venv built from `requirements.txt` resolves the
same versions as long as the lock is current; install the lock instead when
it matters which.

That list used to include torch and sentence-transformers, and scipy behind
them. It does not any more — see "The embedding model runs without torch"
below — and scipy is now declared in `requirements.txt` like the direct
dependency it always was.

**`AWS_DEFAULT_REGION`.** Several modules build a boto3 client at import time.
`lib/aws/region.py` defaults to `eu-central-1` for the application's own use,
but a bare `boto3.client(...)` does not consult it, so collection dies with
`NoRegionError` before a single test runs. No credentials are needed for the
unit suite — only the region.

**`-m "not quality"`.** See below.

## What 3.14 bought, and what it did not

The interpreter move is recorded above as a non-event for test results, which
is what made it safe. This section is the other half: which of 3.14's features
are worth something *here*, measured rather than assumed, so the next person
does not re-derive the list.

**Read the caveat on every number below first.** They were taken in an agent
sandbox on **3.14.0rc2**, because that is the only 3.14 `uv` offers there (the
`uv python list` note at the top of this file). Two consequences. Nothing that
needs pydantic runs at all on it, so no measurement here involves the reader,
the models or the grammars-with-actions; `pydantic==2.13.5` dies on rc2 with
`AssertionError` in `eval_type_backport`. And a 3.13-against-3.14 number
compares Debian's gcc `python3.13` against a python-build-standalone clang
build with PGO, BOLT, LTO and the tail-call interpreter, so it is a
*build* comparison wearing an interpreter's clothes. The numbers taken on one
interpreter against itself are the trustworthy ones, and they are marked.

### The build switches, which were already half-won

`/opt/py314` is whatever `uv python install` resolved, and python-build-standalone
configures it:

```
--with-tail-call-interp --enable-experimental-jit=yes-off --enable-optimizations --enable-bolt
```

Two things follow, and neither was known when the move was made:

- **The tail-call interpreter is already on**, and costs nothing. It is the
  single largest free win in 3.14 for a workload like this one, and it arrived
  by accident of which build uv fetched. Nothing pins it: a base rebuild that
  resolves a differently configured build drops it silently, with no error, no
  failing test and no symptom except latency. `lib.jargon.verify` now prints
  the interpreter's switches in the runtime stage and **warns** when the
  tail-call flag is missing. A warning and not a failure: the image is correct
  without it, and failing a build over a performance switch turns a base
  rebuild into an outage.
- **The JIT is compiled in and switched off**, so `PYTHON_JIT=1` is a lever
  that exists. **Do not pull it.** Measured on one binary against itself,
  which is the clean comparison: GLR parsing through parglare 0.22.0 came out
  **5 to 8% slower** with the JIT on (479us/parse off against 507us on;
  465 against 502 on a repeat), and a tight numeric loop was slower or level
  across four alternating runs. That is the expected shape rather than a
  surprise: this service's Python time is spent in parglare's GLR loop and in
  C extensions (cv2, onnxruntime, pymupdf, faiss), and the tier-2 JIT's
  warm-up is not repaid by either. `verify` reports the JIT's state for the
  same reason it reports the tail-call flag, so a future re-measurement starts
  from what the image is doing rather than from this paragraph's age.

### Adopted

- **asyncio call-graph introspection** (`asyncio.print_call_graph`), in
  `lib/diagnostics/async_call_graph.py`. `loop_stall_monitor` has two
  attributions that report no frame of ours by construction,
  `loop-internal(...)` and `loop-idle(starved-or-gil-contention)`, and for
  those the synchronous stack has nothing left to say: the coroutine that
  asked for the blocking read suspended at its `await`, so its frames are held
  by the task and not by the thread being sampled. 3.14 tracks who awaits
  whom, and the graph can be read **from a non-loop thread**, which is the
  only kind the sampler has. A `loop-internal` stall now carries the in-flight
  tasks and their await chains. It is captured at peak-sample time, not at
  report time, for the same reason the stack is; it is bounded to 24 tasks and
  24 frames; and it is not asked for when a repo frame is already on the loop,
  because there the frame is the answer.

  The limitation is worth knowing before extending it: the graph is recovered
  from *suspended* frames. A task that is currently executing comes back as
  the one frame it is running, which the synchronous stack already reported
  more precisely. So this cannot be made to answer "what is the loop doing",
  only "what was waiting on it".

### Dropped for portability, not for a number

**`cpp_uuid` is gone, on the owner's decision of 2026-09-25.** Until then
it was kept for speed, and the speed was real. What decided it was portability:
`cpp-uuid==1.0.1` ships only an sdist whose `setup.py` passes
`-march=native` after `CFLAGS`, so the image carried whatever the CodeBuild
host supports, AVX-512 included. m5a.large (Zen 1) workers crash-looped on
it on 2026-09-23 (`CORE-READER-17F`) and the spot pool was cut to AVX-512
types (infrastructure `d95c89a`). It went AMD-only the next day for a
different reason, warmup speed (infrastructure `50a8d00`, #227 S-3). Workers
stay full spot and the pool widens, so the dependency went instead.

`crew/utils/uuid.py` returns `str(uuid.uuid4())` from the standard
library, on the owner's decision on #2472 (2026-09-27), with the same
output: a lowercase 36-character `str`, version 4, RFC 4122 variant.
On 3.14.7 against itself, ns per id (min / median of 45 runs of
200,000): cpp-uuid **114 / 120**, `crew.utils.uuid.uuid4()`
**1409 / 1495** (`str(uuid.uuid4())` alone **1379 / 1458**), so about
1.4 us more per id. How many ids a request mints has not been counted:
one per sheet, page, canvas, sectional and variant, and one per exported
measure, GD&T, radius and roughness, so tens for a small drawing and a
few hundred or more for a dense multi-sheet one is an estimate. That is
about 0.04 ms more per request at 30 ids, 0.4 ms at 300 and 4 ms at
3,000, against a read measured in seconds.

The wrapper stays, rather than its 13 callers calling `uuid.uuid4()`
directly, because they expect a `str` (the pydantic `default_factory` fields
in `crew/model/` among them), and a `uuid.UUID` compares unequal to one.
cpp-uuid also kept state of its own that a fork copies: a forked child's
first `cpp_uuid.uuid4()` was the parent's next id, every time. `crew/utils/uuid_test.py` fails on that, and on anything that is not
one `os.urandom(16)` per id, so neither cpp-uuid nor a hand-rolled pool
comes back unnoticed.

`tests/test_no_cpu_specific_build.py` fails if cpp-uuid comes back in a
dependency file or a Dockerfile, if anything imports `cpp_uuid`, or if one
of those files asks for `-march=native`. **It cannot see a flag inside a
dependency's own `setup.py`**, which is exactly where cpp-uuid's was, so
the next package built that way would pass it. Only pycld2 and
alphabet-detector build from source today (pycld2 at `-O2` with no
`-march`; alphabet-detector is pure Python). Installing the lock with
`--only-binary :all:` plus an allowance for audited sdists would close
the gap; nothing does that yet.

**The core-reader pool can take x86-64 types with AVX2 and without
AVX-512 once a release without cpp_uuid is serving** ("Did the merge to
`prod` actually deploy?" below), not at merge: until then the running
image still carries the extension. AVX2 is what was proven: the whole
native import closure ran under an emulated Zen 1 (AVX2, no AVX-512).
CBC is the one native piece not proven on such a CPU. Its coinbrew build
passes no `-march` (read from the configure scripts), but the binary in
the base image was never disassembled. It runs as a subprocess from
`lib/techreader/spec/cell_coupler.py`, and pulp raises `PulpSolverError`
when it exits non-zero, so the confirmation is a successful read with a
title block on a worker with `host.cpu_avx512=no`, and a
`PulpSolverError` from one is the thing to look for. `host.cpu_avx512`
and `worker.started` in Sentry show which types a worker runs on and how
often it restarts.

### Audited and rejected, with the number that decided it

- **`compression.zstd` (PEP 784) on the request cache** is the best unclaimed
  idea here and is deliberately not taken in this pass. `lib/request_cache`
  PUTs raw orjson to S3 and GETs it back under a 2s `LOOKUP_TIMEOUT_SECONDS`,
  so a smaller body buys hit rate, not just storage. It needs a format
  migration (sniff the zstd magic `28 b5 2f fd` so old objects still read) and
  it needs payload sizes nobody has measured. Both are cheap; neither could be
  done on an interpreter that cannot import the reader.
- **`forkserver` for the parse pool.** 3.14 changed the Linux default from
  `fork` to `forkserver`, and `parallel_parser` pins `spawn` explicitly, so
  the change does not reach it (the note above says to keep that argument, and
  this pass keeps it). It is still the largest untaken win in the repo:
  `init_parse_worker` builds four grammar readers in **every** spawned worker,
  4 to 8 of them, each paying a fresh interpreter and a fresh import of the
  world, and the module already logs per-worker RSS precisely because a
  spawned worker shares nothing copy-on-write. A forkserver parent that
  preloads the grammars once and forks would cut both the warmup and the
  footprint. It is a real change with real risk and wants its own PR and its
  own measurement, not a line in an adoption sweep.
- **Free-threading (PEP 779) is blocked by wheels, not by us.** At the pins in
  `requirements.txt`, `opencv-contrib-python-headless` (`cp37-abi3`) and
  `tokenizers` (`cp310-abi3`) publish only abi3 wheels, and a free-threaded
  build accepts no abi3 wheel: on a real 3.14.7t, uv finds no usable wheel
  for either. Building them from source (C++ and Rust) is possible in
  principle and is a project of its own. Revisit when those two publish
  `cp314t` wheels. pycld2 has no wheel for any 3.14 and already
  builds from source here; whether it builds for 3.14t is untried. (`cpp-uuid`
  used to be on this list; #2472 dropped it.)
- **`concurrent.interpreters` / `InterpreterPoolExecutor` (PEP 734)** is the
  natural successor to the parse pool and is not usable yet: every worker
  would still build its own grammars (parse tables do not cross interpreters),
  and the C extensions on the import path must all support multi-phase init.
- **PEP 649 deferred annotations.** 105 files carry
  `from __future__ import annotations`, which is now redundant. Removing it is
  mechanical but it is 105 files of churn with a real failure mode (any file
  relying on stringized annotations to dodge a circular import), and the
  pydantic-side benefit could not be measured on an interpreter pydantic does
  not import. Worth doing deliberately, not as a side effect.
- **PEP 765 (`return`/`break`/`continue` in `finally`)** is a genuine bug class
  and 3.14 warns about it at compile time. All **1874** `.py` files in the repo
  compile on 3.14 with **no `SyntaxWarning` and no `SyntaxError`**, so there is
  nothing to fix. Worth re-running after a large merge; it takes seconds:

  ```python
  import warnings, pathlib
  for p in pathlib.Path(".").rglob("*.py"):
      with warnings.catch_warnings(record=True) as w:
          warnings.simplefilter("always")
          compile(p.read_text(), str(p), "exec")
          for x in w: print(f"{p}:{x.lineno}: {x.message}")
  ```

- **PEP 768 remote debugging** (`python -m asyncio ps <pid>`, `pdb -p`) is real
  and is **not reachable in production**, which is worth writing down before
  someone plans on it. The app image is distroless: no shell, so ECS exec
  cannot open one to run the attaching process from. The await tree adopted
  above is the in-process substitute, and it is why it is in-process.
- Nothing in the repo compresses, so `zipfile`'s ZSTD support is moot;
  `Executor.map(buffersize=...)` appears only in the batch scripts under
  `tests/`; `base64.z85`, `math.fma` and `pathlib.Path.copy` have no call site
  here. `copy.deepcopy` going to C is already covered above under the tests,
  and it remains the one 3.14 change that measurably moved this codebase.

## Running the tests

Two test-file conventions are in use and no single runner sees both by default:

| Where | `test_*.py` | `*_test.py` |
| --- | --- | --- |
| under `tests/` | ~290 | ~26 |
| beside the code, in `crew/`, `anvil/`, `lib/`, `utils/` | ~10 | ~92 |

- `pytest` from the repository root collects all of them (~4200 tests, ~10
  minutes). This is the command to run.
- `pytest tests/`, which the README gives, misses every test that sits next to
  the code — which is usually the one that covers a change to `crew/`, `lib/`
  or `anvil/`.
- `nose2 -c nose_fast.cfg` collects only the `*_test.py` files, because
  `test-file-pattern = *_test.py`. `nose.cfg` is the same file with the
  profiler left on.

`pytest.ini` pins `--import-mode=importlib` and `consider_namespace_packages`.
Do not drop either. `crew/` and `lib/` are namespace packages with no
`__init__.py`, and under pytest's default `prepend` mode every directory holding
a test without an `__init__.py` gets pushed onto `sys.path` — which put `lib/`
there, made `lib/utils` answer to the plain name `utils` and shadow the
repository's own `utils/`, and left `lib/threads/*_test.py` (they import their
neighbours relatively) unimportable. The ini file also pins the rootdir, so
`pytest` and `pytest tests/` resolve module names against the same root.

### The `quality` marker

`tests/quality/base.py::QualityTest` and its subclasses under `tests/customer/`,
`tests/feature/` and `tests/quality/` download real customer drawings from the
`core-reader-assets` S3 bucket and run the full reader — Bedrock calls included
— over them. They need AWS credentials and they cost money per run.

- `pytest -m "not quality"` is the offline unit suite.
- `pytest -m quality` is the benchmark. Run it deliberately, with credentials.

The marker rides on `QualityTest.pytestmark`, so every subclass inherits it and
nothing has to be tagged by hand.

**A local quality run has both result caches off** (`LLM_RESULT_CACHE_ENABLED`
and `REQUEST_RESULT_CACHE_ENABLED`, set in each reading worker before the
reader is imported, after any arm variables so an arm cannot turn one back on),
so a repeat run measures the model and not the cache. Every local run writes
`arm.json` (per-column precision, cost and p50/p95 per file) beside
`precision.json`.

A remote run (`remote = True`, or a suite such as `schott_remote_test.py` that
calls the API itself) is neither. It reads through the deployed service, whose
caches this harness cannot reach, and it writes `precision.json` and the diff
but no `arm.json`, so it cannot be a baseline; `go()` refuses the A/B variables
when `remote` is set.

**To gate a model or prompt change, compare two arms rather than reading the
absolute thresholds** (`tests/quality/ab.py`, #2410):

- A model lever: `QUALITY_AB_CANDIDATE_ENV='{"STRUCTURED_CALLOUTS_MODEL": "..."}'
  pytest -m quality <suite>` reads the suite twice, as deployed and with those
  variables on top.
- A code or prompt change: run the suite on `origin/test` in a worktree, then
  on the branch with `QUALITY_AB_BASELINE=<that run's arm.json>`.

The run fails when a column falls more than `QUALITY_AB_MAX_PRECISION_DROP`
(default 0.02) below the baseline, when the two arms did not read the same
drawings (`arm.json` carries a digest of the set, so a local
`_filter_files.json` or `max_files` on one side shows up), and, when
`QUALITY_AB_MAX_COST_RATIO` is set, when the mean cost per file rises past
that ratio. The cost ceiling is off unless set. `ab.json` holds both
arms and the reasons. A suite method that calls `self.go()` without `await`
passes without reading anything; `tests/quality/test_suites_await_go.py`
fails on one.

## Test isolation: do not stand in for a module that exists

Several test files replace native or heavy modules with stand-ins so an import
chain stays cheap. The guard has to be `importlib.util.find_spec(name) is None`,
never `name not in sys.modules`:

```python
for _native in ("alphabet_detector", "pulp"):
    if _native not in sys.modules and importlib.util.find_spec(_native) is None:
        sys.modules[_native] = MagicMock()
```

`not in sys.modules` is true for any module that merely has not been imported
*yet*, so the stand-in takes the name for the rest of the process and every file
collected afterwards tests against a `MagicMock`. This was not hypothetical:
one file installed a `crew` stub with an empty `__path__` and unrelated modules
then died on `No module named 'crew.model'`, and another replaced `settings`
wholesale so twelve later files could not import `AWS_ACCOUNT_ID` from it. Both
moved with collection order, which made them look like flaky tests somewhere
else. `tests/lib/cost_tracking/test_metric_cardinality.py` carries the canonical
comment.

For the same reason, do not add `sys.path.insert(...)` to a test file. The
rootdir is already importable.

## Known-red tests

Until #2411 nothing in CI ran these tests, so the suite carries a backlog.
`.github/workflows/unit.yml` now gates a pull request on the ids it newly
fails, not on the backlog. The last full run of

```
AWS_DEFAULT_REGION=eu-central-1 pytest -m "not quality" --continue-on-collection-errors
```

was **127 failed, 4306 passed, 20 skipped, 15 deselected, 4 collection errors**
in 11m26s, measured on `test` at `134f28da` (2026-09-18); **126 failed, 4319
passed, 20 skipped, 15 deselected, 4 collection errors** in 10m07s on
`118ade0b` (#2196, the same day; that run was diffed by id against the
branch's own previous run, not against the `test` run); and **127 failed, 4410
passed, 20 skipped, 15 deselected, 4 collection errors** in 18m03s at
`1a4d0d22` (2026-09-20), measured in a `git worktree`, so one lower than the
same commit run in place — but that asymmetry is gone now, see the venv note
under "Before you push".

The most recent pair, both on 2026-09-20 and taken against each other:
**127 failed, 5021 passed, 22 skipped, 15 deselected, 4 collection errors** in
11m22s on `test` at `55db744a`, measured in a `git worktree`; and **127
failed, 5031 passed, 22 skipped, 15 deselected, 4 collection errors** in
16m06s on #2245, cut from that commit and measured in place. The failing ids
diffed to **nothing in either direction** — 131 identical lines, 107 `FAILED`
plus 20 `SUBFAILED` plus 4 `ERROR` — and the 10 passes are that branch's own
new tests. The two wall times are the same suite on the same machine with one
run loaded and one not; they are not a signal.

The jump from 4410 to 5021 passes is ten `test` merges in between, not a fix:
the failed count did not move at all across it.

Then the dead code came out (#2250), and both halves of that pair were
measured in place on the same machine: **129 failed, 5107 passed, 22 skipped,
15 deselected, 4 collection errors** in 14m36s on `test` at `e559297d`, and
**123 failed, 5106 passed, 22 skipped, 15 deselected, and no collection
errors** in 9m02s on the branch. The failing ids diffed to ten gone and none
gained. Nine of the ten are the files that branch deleted; the tenth is
`test_the_blocking_function_is_named`, the timer-sampled test listed below
that moves on its own. **The four collection errors are gone for good** --
they were the two dead files, and the two dead files no longer exist. A
collection error in a run from here is yours.

That run was also five minutes shorter, but do not read anything into it: the
wall time on this suite has swung from 8m28s to 14m40s on its own, and the
deleted tests were failing fast rather than running long.

### A baseline measured with `test_jargon_reader_integration.py` ignored

A different measurement shape, and it does not compare against anything above.
On 2026-09-21, on `test` at `0afdc0c7`, in a `git worktree`:

```
AWS_DEFAULT_REGION=eu-central-1 pytest -m "not quality" \
  --continue-on-collection-errors --ignore=tests/test_jargon_reader_integration.py
```

**118 failed, 5026 passed, 22 skipped, 15 deselected, no collection errors**
in 3m41s.

Two reasons to have it. The `--ignore` is the one this file already
prescribes further down, because a whole-repo run **stalls** in that file --
its hypothesis cases spawn and tear down a process pool per example. That is
not a figure of speech: a run started without it sat at 80% for fifty minutes
on 2026-09-21 and had to be killed, having produced nothing. And the 3m41s
against the 9-to-14 minutes recorded above is almost entirely that one file,
which is worth knowing before budgeting an afternoon for a baseline.

Compare an `--ignore` run only against another `--ignore` run. The counts
above are eleven lower on `failed` than the previous entry for reasons that
include the ignored file's own failures, so subtracting them against a
whole-repo run manufactures exactly the off-by-eleven this section exists to
prevent.

#### The pair that moved the runtime to 3.14

Both in the same shape as above (`--ignore`, plus `-p no:cacheprovider`),
taken against each other on 2026-09-21, in place, one after the other rather
than side by side, from two venvs whose `pip freeze` output is byte-identical,
with `.hypothesis/` removed before each. Three times, because `test` moved
twice while this was being measured:

| Base | 3.13.12 | 3.14.7 | ids |
| --- | --- | --- | --- |
| `7760127b` | 118 failed, 5027 passed | 118 failed, 5027 passed | identical |
| `d94fd29d` merged in | 118 failed, 5106 passed | 118 failed, 5106 passed | identical |
| `a569d2a3` merged in | 118 failed, 5150 passed | 119 failed, 5149 passed | one extra, see below |

(22 skipped, 15 deselected and no collection errors throughout.)

The passes climb because `test` kept adding tests -- 79 then 44 -- while the
failed count stood still across all of it. That is the shape this section
keeps warning about, and the reason to diff ids rather than counts.

The third pair's one extra id is
`tests/test_pandas_upgrade.py::TestPandasUpgradeProperties::test_csv_round_trip`,
and it is **not** an interpreter difference, though it looks exactly like one
until you pin the seed. See its entry below; the short version is that the
same `--hypothesis-seed` gives the same verdict on both interpreters, and the
eight test files that merge added pass 74/74 identically on both.

`test` then moved 34 commits again, to `48899460`, and that one was **not**
re-measured as a full pair. It did not need to be: the diff from `a569d2a3`
touches no dependency file, neither Dockerfile and no workflow, so nothing in
it can interact with the interpreter except through a test. The 19 test files
it added or changed were run on both instead -- 255 passed, 3765 subtests
passed, identical on 3.13 and 3.14.

**That is the cheap check, and it is the one to use when this branch goes
stale rather than another ten-minute pair.** On a release day `test` here
takes tens of commits an hour, so a full pair can never catch up with it; what
a full pair buys over the targeted run is coverage of an existing test that a
*non-test* change made interpreter-sensitive, which is a narrow enough case to
spend ten minutes on deliberately rather than on every base move.

**And count files, not commits, when you size a base move.** On 2026-09-21
`test` merged #1962 and #1988, two long-lived branches whose ancestry predates
a history rewrite, and `git rev-list --count HEAD..origin/test` jumped from 4
to **4336**. That number is ancestry, not content: the same range touched 14
test files and no dependency, Dockerfile or workflow file at all, and the
merge was clean. So a four-figure "behind" count here is not necessarily a
reason to re-measure anything, and

```
git diff --stat $(git merge-base HEAD origin/test)..origin/test -- \
  requirements.txt requirements-dev.txt Dockerfile Dockerfile.base .github/workflows/
```

is the question worth asking instead. (Targeted run on those 14 files after
the merge: 301 passed, 48 subtests passed, identical on 3.13 and 3.14.)

So the failing ids diff to **nothing in either direction** on two independent
bases 18 commits apart, and the third disagreement is a seeded coin. That is
the claim the interpreter move rests on, so it is worth saying
what it cost to get a diff that clean, because the first three attempts each
came back at 119 and each one was a different thing:

- `test_a_stall_inside_a_library_is_attributed_to_our_caller` failed twice,
  for two unrelated reasons, and only the first was about 3.14. Both are
  described in its entry below; both are fixed in the same commit as this
  measurement.
- `tests/test_pandas_upgrade.py::TestPandasUpgradeProperties::test_excel_round_trip`
  failed once, because an *earlier* run in the same checkout had found the
  counterexample (`"INFINITY"` read back out of Excel as `inf`) and left it
  in `.hypothesis/`. It then failed identically on 3.13 -- same shape as
  `test_spatial_matcher` below. **Remove `.hypothesis/` before a baseline
  pair**, or the second run inherits whatever the first discovered and the
  diff reports an interpreter difference that is really a cache.
- `tests/test_plt_importer.py::...::test_the_decode_starts_before_textract_answers`
  failed once, on the run that also took 6m38s. It is the documented
  wall-clock flake below, passed 10/10 in isolation on both interpreters, and
  was the machine being busy rather than anything about 3.14.

Do not read the wall times as a 3.14 speedup either way: these two are within
the noise this suite generates on its own (8m28s to 14m40s across runs of the
same tree), and the first run of a pair also pays the `.pgc` rebuild described
under "Two things a test run leaves behind". The counts are the signal.

#### A pair after that, on 2026-09-21

Same shape again (`--ignore`, `-p no:cacheprovider`), `.hypothesis/` removed
before each, base in a `git worktree` and branch in place, one after the
other. Measured on **3.13.12, not 3.14**, for the reason in the `uv python
list` note at the top of this file:

| | failed | passed |
| --- | ---: | ---: |
| `test` at `993a9163` | 118 | 5499 |
| #2288, merged from it | 119 | 5501 |

(22 skipped, 15 deselected, no collection errors on both.) The 2 passes are
that branch's own new tests. The one extra failing id is
`test_csv_round_trip`, and it is the unseeded coin below rather than anything
the branch did: with `--hypothesis-seed` pinned, seeds 1 to 5 pass on **both**
trees and seed 6 fails on **both**, which reproduces the verdict the pair
above recorded, on a different pair of runs and a different axis. The two
`test_loop_stall_attribution` siblings swapped places on an earlier run of
that branch against `35bfec33` and are green on both sides here, so the fix
that shipped with the interpreter move holds.

Write that number down again whenever it moves; without it there is no way to
tell a failure you caused from one that was already there. The same headline
can hide a move — and a headline that moves is not always a break: across those
three the passed count gained a hundred while the failed count stood still,
which was new test files rather than fixes. Diff the failing test ids, not the
counts.

And diff the FAILURES before the passes. `passed` moves whenever anyone adds a
test *or* whenever the base moves under you, so it carries no signal on its
own: #2229 merged `test` and measured **126 failed, 4562 passed, 20 skipped,
15 deselected, 4 collection errors** in 10m15s, where the 4562 is 4319 plus its
own 72 tests plus everything `test` gained in between. The failing ids diffed
to two fixed (two grammar tests) and one gained
(`test_suppress_unsupported_format_sentry.py::TestPreservationOtherInternalExceptionsSentryReporting::test_other_internal_exceptions_still_logged`),
and that one reproduces on a clean `origin/test` worktree, so it is the base's.

And re-measure on your OWN base when the recorded commit is not it. On
2026-09-20 a branch cut from `8504ed6e` measured **128 failed, 4305 passed,
20 skipped, 15 deselected, 4 collection errors** in 11m49s; against the
`134f28da` entry above that reads as one failure introduced, and against a
run of `8504ed6e` itself it is exactly zero — the four commits in between
include one that adds test files. A baseline from a different base answers
nothing. (Both of those runs were taken in place, in a checkout carrying its
own `.venv`, so both include the venv-inside-the-repo failure described at the
end of this file. Comparing an in-place run against a worktree one is the
other way to manufacture an off-by-one.)

### A stale virtualenv reads as a catastrophic regression

`requirements.txt` installs `werk24` from that repository's **main branch**,
unpinned. So a venv built last week silently holds a different library from the
one `test` is written against, and nothing tells you: the failure surfaces as a
mass collection error with no mention of werk24 in most of the lines.

Measured on 2026-09-20, on a venv that predated werk24-python `c3b96d5`:
**339 failed, 2259 passed, 226 errors** — against a true result of 126 failed
and 4 errors on the same working tree. Only 84 of those errors name the real
cause (`cannot import name 'MaterialOrigin' from 'werk24.models.v2.enums'`);
the other ~170 are `No module named 'crew.model.canvas'` and friends, which is
the stand-in trap above cascading off the first failure and points nowhere near
werk24.

So before believing a run that is dramatically worse than this file says:

```bash
uv pip install -q --python .venv/bin/python --upgrade \
  "werk24 @ git+https://github.com/W24-Service-GmbH/werk24-python.git"
```

and run it again. A change merged into werk24-python main reaches this
repository with no version bump and no lockfile change, which is the same
property that makes a breaking model change there land in five repositories at
once.

Where the 126 sit: 47 in the Weidmann prompt and LLM suites, 20 in the jargon
grammars, 11 under `tests/application/`, 4 in the xometry configurator formats,
and the rest scattered singly (the `test` run counted 23 grammar files and 22
scattered). The four collection errors were the two dead files and the 11
under `tests/application/` were the dead application suites; #2250 removed
both, so a run from here has neither. Only 106 of the 126 appear as `FAILED`
lines; the other 20 are `SUBFAILED(...)` lines, one per failing `self.subTest`
block, and pytest 9 reports their containing test as **passed** (three ids
here, in `unsupported_format_error_test.py` and the two
`weidmann_blue_prompts` runners), so grep for `SUBFAILED` too when you
are diffing a run against this. A test written against the function-style
`subtests` fixture behaves differently: it gets a `SUBFAILED` line per failing
subtest *and* a `FAILED` line for the container, and the summary counts both,
so there the two lists overlap rather than add up. Measured on pytest 9.1.1
with one test of three subtests, one failing: `1 failed, 1 passed` for the
unittest form, `2 failed` for the fixture form.

Three of them move on their own, so a count that differs by one or two from
this is not necessarily your branch. A fourth used to and no longer does; it
is still listed first, because what stopped it is the thing to know:

- **`tests/test_cost_tracking_fixes.py::test_no_caller_nets_cached_tokens_out_of_input`**
  used to fail whenever the virtualenv sat inside the repository — which is
  what the setup at the top of this file tells you to do. It globs `**/*.py`
  from the repository root with no exclusion beyond `.git`, so it reached
  `.venv/lib/python3.13/site-packages/joblib/test/test_func_inspect_special_encoding.py`,
  which is big5-encoded, and died on `read_text(encoding="utf-8")` before it
  could check anything.

  **It passes in place now, and the reason is worth knowing: joblib is no
  longer installed at all.** It arrived behind scikit-learn, which came behind
  sentence-transformers, and all three left with the torch removal — so the
  big5 file the glob tripped over is not on disk any more. Measured on
  2026-09-20 on a venv inside the repository: the test passes, and
  `import joblib` raises `ModuleNotFoundError`.

  The glob is still unbounded, so this comes back the moment any dependency
  ships a non-UTF-8 file under `.venv/`. It is no longer a reason to expect a
  difference between an in-place run and a worktree one.
- **`tests/lib/diagnostics/test_loop_stall_attribution.py::TestTheStallIsAttributed::test_a_stall_inside_a_library_is_attributed_to_our_caller`**
  samples the loop thread's stack on a timer, so it fails on a loaded machine
  and passes on an idle one. It passes in isolation either way. Its sibling
  `test_the_blocking_function_is_named` turns on the same timer: on
  2026-09-18 it passed and then failed in two consecutive runs alone on the
  same tree, and passed with the rest of its file.

  **Both of those should be stale now** (2026-09-21, the 3.14 move). Two
  separate things were wrong with this file and both are fixed:

  - It blocked the loop with a fixed 60 `copy.deepcopy` calls, which take
    ~180ms on 3.13 and ~57ms on 3.14, where `deepcopy` is C. Under the 100ms
    threshold the sampler saw no stall, logged nothing, and the test failed
    with `no logs of level WARNING` -- an assertion about the *setup*, saying
    nothing about the attribution logic the test exists for. The block is
    deadline-driven now, as its sibling's already was. **A test that has to
    stall something should be driven from a clock, not from an iteration
    count**; an interpreter upgrade silently retunes the second kind.
  - The flakiness itself had a cause, and it was not just "a loaded machine".
    The sampler keeps its highest-age observation and reports on the recovery
    edge, so any sampler tick landing after the block returned but before the
    loop's next `note_tick` overwrote a good in-block sample with the idle
    `run_until_complete` frame -- reported as `at=...(_run)`. That window is a
    few milliseconds against a 20ms sampling interval, which made it a flake
    rather than a failure: about one whole-file run in twelve, on 3.13 and
    3.14 alike. The blocking callbacks beat the heartbeat themselves now, on
    the loop thread, the instant they return, which removes the window instead
    of narrowing it. Measured after: 15 whole-file runs green on each
    interpreter, with and without `PYTHONASYNCIODEBUG` set.

  That second one has a tail worth knowing: asyncio debug mode widens the
  window, because asyncio logs the slow callback before the tick coroutine
  gets control back -- and debug mode is **on** for most of this suite by
  accident. `tests/test_external_dimensions.py` sets
  `os.environ["PYTHONASYNCIODEBUG"] = "0"` at import, and `bool("0")` is
  `True`, so that line turns asyncio debug on process-wide for every test
  collected after it rather than off. It is not this file's problem any more,
  but it is still a live confound for anything else timing-sensitive.
- **`tests/test_plt_importer.py::PltDecodeOverlapsOcrTest::test_the_decode_starts_before_textract_answers`**
  was on this list from 2026-09-21 as a wall-clock flake with generous
  headroom. **That diagnosis was wrong and the test is fixed** (#2253); it
  should not move again, and the reason is worth more than the entry was.

  The test waits for the decode to start with
  `asyncio.wait_for(decode_started.wait(), timeout=5.0)`, and the stand-in
  signalled that Event with a plain `decode_started.set()` — from a CPU_POOL
  worker thread, because that is where `to_cpu_thread` runs it.
  `Event.set()` resolves its waiters through `loop.call_soon`, which appends
  to the ready queue *without* writing to the loop's self-pipe, so a loop
  asleep in `select()` never learns. The waiter then stays parked until
  something else wakes the loop — which here is the decode's own executor
  future completing.

  So it waited for the decode to FINISH while claiming to wait for it to
  START. Measured through the real `to_cpu_thread`, with the event set 200ms
  in (old / fixed):

  | | old | with `call_soon_threadsafe` |
  | --- | --- | --- |
  | decode 2s, deadline 5s | woke at 2201ms | 200.8ms |
  | decode 8s, deadline 5s | woke at 5007ms | 200.7ms |

  The second row is the flake: the waiter resolves at the very instant the
  timeout fires, so whether `wait_for` returns or raises comes down to which
  callback the loop runs first. That is why the failing traceback showed the
  Event as `<asyncio.locks.Event object ... [set]>` — the decode *had*
  started; nothing had woken the loop to say so. A slow machine did not cause
  this, it only made the decode long enough to reach the deadline.

  **Signal an asyncio primitive from a non-loop thread with
  `loop.call_soon_threadsafe`, never by touching it directly.** A test that
  gets this wrong does not fail; it silently waits for the wrong event and
  passes for years, then moves under load.

  The neighbouring lesson still holds on its own account: **do not run two
  full suites concurrently on one box.** `test_loop_stall_attribution` above
  is a genuine wall-clock assertion, and contention is enough to turn it red.
  A baseline in a worktree is meant to run *instead of* your branch's run,
  not beside it.

  `tests/lib/techreader/request/test_drawing_prefetch.py::DrawingPrefetchTest::test_a_prefetch_for_another_uri_is_ignored`
  went the same way in #2253 and never reached this list. It asserted the
  prefetch file was gone after a single `await asyncio.sleep(0)`, but
  `discard()` only unlinks inline once the download has finished; while the
  GET is still in flight the removal belongs to `_download`'s `finally`, on
  the worker thread. One tick is enough only when that thread happens to have
  returned. It waits for the task now, as every other test in that file
  already did.
- `tests/test_spatial_matcher.py::test_word_to_annotation_assignment_maximizes_overlap`
  (#2199, a wrong test oracle) fails only in a checkout whose `.hypothesis/`
  database holds the counterexample.
- **`tests/test_pandas_upgrade.py::TestPandasUpgradeProperties` is a genuinely
  unseeded flake, and it is the one most likely to be mistaken for a real
  regression.** Two of its property tests, `test_excel_round_trip` and
  `test_csv_round_trip`, share a wrong oracle:
  `assert_dataframes_equivalent` handles several round-trip coercions but not
  a numeric-looking *string*, and both CSV and Excel read one back as a
  number. `"INFINITY"` comes back as `inf`, `"0E0"` as `0.0`, `"nan"` as
  `nan`. Measured directly on both interpreters, the coercion is identical --
  it is pandas, not Python.

  Nothing pins the seed, so whether a run finds such an example is chance.
  That produces two different-looking failures:

  - **Within a checkout**, once a run has found one it lands in
    `.hypothesis/` and every later run replays it, on either interpreter,
    until that directory is removed. Remove it before a baseline pair.
  - **Across a pair**, one run can find one and the other not, which reads
    as an interpreter difference and is not. Seen at 0/10 against 2/10 on
    2026-09-21, which looks damning until you pin the seed: with
    `--hypothesis-seed` fixed, seeds 1-5 pass on **both** 3.13 and 3.14 and
    seed 6 fails on **both**.

  `--hypothesis-seed=N` is the tool for telling this apart from a real
  difference, and it is worth reaching for before believing any one-test gap
  between two otherwise identical runs. Fixing the oracle would be better.
- `tests/test_jargon_reader_integration.py::TestErrorPropagation::test_grammar_parsing_error_includes_original_text`
  is a Hypothesis test with the default 5s deadline, and its first example
  pays the lazy grammar load (20 to 30s whenever the `.pgc` tables are not
  there or not this checkout's, see below — which on a fresh clone is
  always, since they are no longer committed). It passes when an earlier
  test in the same process loaded the
  grammars, fails alone and fails on a clean `test` checkout; it is order,
  not code. It was red in the `f600cb7f` run and green in the `118ade0b` one,
  with no change to the code it touches.

The previous records, for comparison: 128 failed and 4311 passed at `f600cb7f`
on 2026-09-17 (`item_number_test.py` left the list at `118ade0b`), 127 failed
and 4288 passed at `7672afab` and 127 / 4282 at `2f043cd4`, both earlier the
same day (the view grammar left the list at the first, the anchored-runner
tests added 23 passes at the second), and before that 131 failed and 4064
passed in 8m28s. Passes rose by 218 across #2164, #2187, #2192 and #2193,
which is why the run also got three minutes longer.

Note that pytest's summary counts more failures than there are `FAILED`
lines — on one run, 130 against 110. The difference is subtests: a failure
inside one reports on its own `SUBFAILED` line, which the summary counts
individually and a `grep -c FAILED` does not see at all. Compare the counts
against the counts, or the gap reads as twenty failures that do not exist.

The wall time is not a constant either and is not worth comparing between
machines: the same suite has run in 8m28s, 11m26s and 14m40s. The counts are
the signal.

And one thing that makes a comparison lie whatever the counts say:

- **Diff the lists, not the counts.** Two runs can agree on a headline and
  disagree about which tests produced it, and a missing dependency changes the
  error count without touching any code. So:

  ```
  grep -E "^(FAILED|SUBFAILED)|^ERROR [^ ]" run.txt | sed 's/ - .*//' | sort
  ```

  Why `SUBFAILED` has to be in there is above. `ERROR` needs the `[^ ]` after
  it, and that is not fussiness: pytest prints captured log records at the
  start of a line too, so a bare `^ERROR` also matches every
  `ERROR    root:request_reader.py:564 ...` in the output. On
  `tests/lib/techreader/` that is 66 lines of log against 2 real results, and
  the "diff" is then mostly noise that moves between runs on its own.

  The single space is what separates them, so match on that rather than on
  the path. A collection error is `ERROR <path>::<id>`; a log record pads the
  level to a column and so always has several. Anchoring to `^ERROR tests/`
  instead looks tighter and quietly drops the ones that matter most: plain
  `pytest` collects the ~100 tests that sit beside the code, so a broken
  import there is reported as `ERROR lib/...` or `ERROR crew/...`.

**The jargon grammar count is now 18, not 22** (#2203). `pytest lib/jargon` is
the command that isolates it, and it finishes in under a minute — use it rather
than re-running the whole suite to tell a grammar failure apart from one you
caused. The total was not re-measured: a whole-repo run stalls in
`tests/test_jargon_reader_integration.py`, whose hypothesis cases spawn and tear
down a process pool per example. `--ignore` that file to get a run that
finishes.

As of that run: 

- **Grammar suites** under `lib/jargon/reader/assets/raw/**/grammar/*_test.py`
  fail on individual phrases (for example `RAD. 4` no longer reads as `R4`).
  These are content gaps in the grammars, not environment problems — they load
  the raw `.pg` file directly and need no compiled assets. The
  `grammar-gap-review` skill is the process that works this backlog down.

  Not all of them are content gaps, though. These tests parse the fragment
  grammar on its own, and production never does. Two things differ, and both
  matter:

  - The master grammar wraps every part in `expr: clutter* space parts space`
    and the reader pads the text, so a part is always delimited on both sides.
    That envelope rejects partial matches the fragment accepts — `ASDFASDF`
    reads as item number `ASD` against `item_number.pg` and as nothing against
    the callout master.
  - `_prepare_grammar_text` substitutes the callout tags first, so the grammar
    sees `{SQUARE}` and `{DIAMETER}` where the drawing said `SQ` and `DIAM`.
    Several rules are written against the substituted form and cannot match
    the raw text at all.

  So check a failure with `await read_callout(text, CALLOUT_LOCK)`, which is
  the whole path. **Not** `run_grammar_unprotected`: it applies the envelope
  but not the substitution, so it under-reports — `R4 TYPICAL`, `1mini` and
  `eØ 20 -0.1` all look broken through it and are fine through
  `read_callout`.
- **Weidmann prompt suites** (`tests/test_weidmann_*.py`,
  `tests/weidmann_blue_prompts/`) assert on prompt text and on LLM output.
  The prompt-text ones drifted from the prompts; the LLM ones need Bedrock.

- **Batch scripts shaped as tests.** There are none left. `test_deva_batch1`,
  `test_deva_ring_batch`, `test_weidmann_auto`, `test_hollister_auto` and
  `tests/test.py` read drawings from hard-coded paths under `/home/jay/` and
  went in #2250, along with the one test in `tests/test_export_balloons.py`
  that did the same (the other ten in that file are mocked and pass). The
  `local_path` override in `tests/customer/cnc24/main_test.py` went with them,
  so that benchmark fetches from S3 like every other quality test, and
  `tests/base.py` resolves the `x://` scheme through
  `W24_DEV_DOWNLOADS_DIR` -- the same base `lib/techreader/request/request.py`
  uses -- rather than one machine's Downloads folder.

  A new one is worth a question. A test that only runs on the machine that
  wrote it is a failure everybody else has to learn to ignore, which is how
  the backlog above got its size.

A failure in one of these is pre-existing. Fix it if your change is about it;
do not treat it as something your branch broke.

## Two things a test run leaves behind

- **`*.pgc` files.** parglare writes its compiled parse table next to each
  `.pg` grammar, so a grammar test run rewrites around 55 of them and creates
  another 55. **They are ignored now and need no cleanup.** Fourteen used to
  be tracked, from before the `compiled/` ignore rule existed, and the
  instruction here used to be to `git checkout -- '*.pgc'` after every run.
  All fourteen were untracked on 2026-09-22 and `*.pgc` was added to
  `.gitignore`, which only bites once nothing matching it is tracked.

  Why they should never have been committed, which is worth knowing before
  anyone adds one back: parglare fingerprints a table against the **absolute
  path** of every grammar file in its import closure
  (`parglare.tables.persist.grammar_fingerprint` hashes `str(path.resolve())`
  alongside the contents). A table committed from someone's checkout is
  therefore refused in `/app`, where the image runs, however identical the
  grammar bytes are. And a refusal is not an error: parglare recomputes,
  which measured **30.9s** for the two masters (callout 19.7s, cell 11.3s) —
  paid in *every* spawned parse worker, which lengthens every worker start
  by that much. Measured locally it did **not** starve the parent's event
  loop: four workers recomputing both tables for 62s on two pinned CPUs left
  a 100ms asyncio ticker in the parent with a worst lag of 36ms (2026-09-24,
  #2306). The ~50s `loop-idle(...)` stalls production reported on every
  worker start on 2026-09-22/23 were the stall sampler reading a heartbeat
  stamped at import, and the receipts lapsing beside them were workers dying
  mid-message. The lag monitor now runs through the startup warmups, so a
  real stall there would be logged as one.

  `tests/lib/jargon/test_compiled_assets_untracked.py` fails if one is tracked
  again. The image builds its own in `python -m lib.jargon.compile` and
  `lib.jargon.verify` checks there, as the runtime uid, that they load.

  A detailed `git checkout -- '*.pgc'` / `git clean -f -- '*.pgc'` procedure
  stood here until the same day, added because `git checkout` alone leaves
  every newly created table as `??` and `git status` never comes clean. That
  is all moot now: an ignored file is neither restored nor listed nor swept
  up by `git add -A`, so a grammar run leaves the tree clean with no
  commands at all. If you remember the procedure, that is why it is gone.
- **`tests/out/`** and `debug_output/`, both already ignored.

## The compiled jargon assets are not in git either

The same reasoning as the parse tables, applied to the other 53 files that sat
beside them. `lib/jargon/reader/assets/compiled/` is entirely what
`python -m lib.jargon.compile` writes: the two master grammars, five reader
and tag-reader pickles, the FAISS index, the symspell dictionaries,
`coupler.json`, `process_map.json`, and a byte copy of all 24 files in
`raw/prompts/`. 59 MB, on top of the 34.7 MB of `.pgc` that went first. All of
it was untracked on 2026-09-22; `.gitkeep` is the one tracked path left, and
it is what keeps the directory in a fresh checkout.

`.gitignore` had covered the whole directory all along. The 53 predate the
rule, and an ignore rule does not apply to a file git already tracks — the
third time that has been the answer here, after the embedding model's assets
and the `.pgc`.

**The image never received them.** `.dockerignore` keeps the tree out of the
build context, so `COPY lib /app/lib` cannot carry it in, and `Dockerfile`
runs the compile regardless. So the committed copy was never what production
read. It was a second, unverified copy, and it drifted: both master grammars
carried an import order `_compile_grammar` had stopped producing, found only
when someone regenerated them by hand (#2322).

**What it cost to remove: a checkout cannot read a drawing until it
compiles.** That is the whole of the trade, and it is why the tree was
committed in the first place.

```bash
sh utils/fetch_embedding_model.sh      # once; docker, or torch
AWS_DEFAULT_REGION=eu-central-1 .venv/bin/python -m lib.jargon.compile
```

**The unit suite does not need that.** Ten test files read a compiled asset,
and `tests/compiled_assets.py` sorts them into three tiers, because they are
four orders of magnitude apart in what they cost to produce:

| Tier | What | How a test gets it |
| --- | --- | --- |
| `compiled/prompts/` | a `shutil.copy2` of `raw/prompts/*.md` | `ensure_prompts()`, milliseconds |
| the two masters | 89 raw grammars concatenated, plus their LR tables | `ensure_masters()`, ~31s once per checkout |
| everything else | embeds every jargon tag, so it needs the ONNX encoder | `requires(...)` / `have(...)`: the test skips |

Only the third tier skips, and only in two files
(`test_tag_layer.py`, `test_callout_parse_dedup.py` — 10 tests). Name the
asset a test actually opens: a test that skips for an asset it never reads has
stopped running for the wrong reason, and nothing will say so.

Measured on 2026-09-22 at `035bcf1b`, on 3.13.12, in the shape this file
prescribes (`--ignore=tests/test_jargon_reader_integration.py`,
`-p no:cacheprovider`, `.hypothesis/` removed):

| | failed | passed | skipped |
| --- | ---: | ---: | ---: |
| before, tree committed | 120 | 5759 | 29 |
| the same tree deleted, before this change | 240 | 5710 | 29 |
| after, on a checkout that has never compiled | 120 | 5750 | 39 |

The failing ids diff to nothing in either direction between the first and
third rows, which is the claim this rests on; the passed counts differ and
reconcile exactly, 5759 + 1 - 10, the replacement test file's extra test less
the ten that skip. **Check that arithmetic rather than the headline.** A
`passed` that moves by ten with `failed` standing still is what a working
skip looks like and also what ten tests silently ceasing to run looks like,
and this table is the only place the difference is written down.

The middle row is what the change had to fix: 122 new failing ids across 10
files, which is what a fresh checkout would have hit.

One production module had to move for this. `raw/process/tag_converter.py`
opened `compiled/process_map.json` in its **module body**, so the import — not
the test — was what failed when the file was absent, taking out every test
collected from the same module. It reads on first use now. A compile still
finds the file, because `compile_process_tree` runs before
`compile_tag_converter` imports it.

## The embedding model runs without torch

`lib/jargon` embeds jargon tags with `intfloat/multilingual-e5-small`. It used
to do that through `sentence_transformers`, which meant torch, transformers
and scikit-learn in every image and on every ECS host, for what at inference
time is one encoder forward pass, a mean pooling and an L2 normalisation.
scipy stays — five modules on the read path import it directly — but it is
pinned in `requirements.txt` now instead of arriving behind scikit-learn.

The model now ships as ONNX. Three moving parts:

- **`utils/export_embedding_onnx.py`** is the only file left that imports
  torch. It downloads the model, traces the encoder to ONNX, and writes
  `model.onnx`, `tokenizer.json` and `embedding_config.json`. The config is
  read off the real SentenceTransformer pipeline — pooling mode, whether it
  normalises, the sequence limit, the padding token — so the runtime never
  guesses.
- **`lib/jargon/reader/utils/onnx_embedding.py`** loads those three files and
  serves `encode()` and `get_sentence_embedding_dimension()` on ONNX Runtime.
  It depends on numpy, onnxruntime and tokenizers, and nothing else — not even
  the rest of `lib.jargon`, which is what lets the export stage load it.
- **The `embedding-export` stage in `Dockerfile.base`** runs the export in a
  throwaway container and leaves the three files at
  `/home/worker/embedding_model` in the base image. The app image points
  `EMBEDDING_MODEL_DIR` at them and installs `onnxruntime` instead of torch.

Four things are worth knowing before touching any of it.

**The model lives in the base image, and that is deliberate.** It was in the
app build at first; it moved on review of #2228. Two reasons. An app build no
longer installs torch or downloads from HuggingFace, which is minutes off
every build. And the ~450 MB model is a layer of the *base* image, which ECS
hosts already have, instead of a fresh 450 MB layer in every app image, which
they would have to pull on every deploy.

The cost is a hard ordering dependency, and it is the kind that bites
silently, so it is worth stating plainly: **nothing rebuilds the base image
automatically.** Changing `EMBEDDING_MODEL_NAME` does nothing to production
until someone runs `utils/build_new_base.sh` and an app image is built on the
result. An app image built on a base that predates the model fails its
`lib.jargon.compile` step, with an error that names the base rebuild.

**The assets are not in git.** `lib/jargon/reader/assets/compiled/embedding_model/`
used to carry eight tracked files — the SentenceTransformer's `modules.json`,
`config.json`, a 17 MB `tokenizer.json` and the model card — committed past the
`.gitignore` rule that covers the whole `compiled/` tree (ignore rules do not
apply to files already tracked). Nothing read them without the weights, which
were never committed, and nothing reads that format at all now. They are gone;
the directory is created by the Docker `COPY` and by a local compile.

**There is no runtime download any more.** `make_embedding_model()` used to
fall back to fetching ~470 MB from HuggingFace when the compiled assets were
missing. It raises `EmbeddingAssetError` instead. The assets are a build
artefact; their absence is a build problem, not something to paper over inside
a customer request.

**A wrong encoder does not raise.** The FAISS indices under
`assets/compiled/faiss` are built at image-build time by embedding every
jargon tag, and the reader queries them with the same encoder. If the two
disagree, nothing errors — the neighbours just get worse, and it surfaces days
later as a read-rate regression. That is why the export refuses to ship a
graph that disagrees with sentence-transformers by more than 1e-4
(`export_embedding_onnx.py::_verify`, which fails the base image build), why
the app Dockerfile sets `EMBEDDING_MODEL_DIR` *before* `lib.jargon.compile`
runs, and why `tests/test_no_torch_at_runtime.py` asserts that ordering along
with the invariant that torch never reaches a base image's published stage.

Changing the model means changing `EMBEDDING_MODEL_NAME` in
`lib/jargon/compile.py` and `DEFAULT_MODEL_NAME` in the export script
together — the Dockerfile cannot read a Python constant, so the image exports
via the script's default while a local compile passes the other one. A test
asserts they match. If the new model's pipeline has a module the export does
not reproduce (a Dense head, say), the export exits with that module named
rather than silently dropping it.

### Getting the model onto a dev machine

```bash
sh utils/fetch_embedding_model.sh
```

**You only need this to run the reader or to rebuild the compiled jargon
assets.** The unit suite does not touch a real model:
`tests/lib/jargon/test_onnx_embedding.py` builds its own four-dimensional
ONNX graph, and the one test that wants the real thing skips. So
`pytest -m "not quality"` needs nothing from that script.

It tries two routes and prefers the cheap one:

1. **Copy it out of the base image** (`docker create` + `docker cp`). Needs
   docker, and gives you the exact artefact production runs — no torch, no
   HuggingFace, no re-tracing, and no chance of a local export differing from
   the deployed one.
2. **Export it here**, which needs torch and sentence-transformers.
   `requirements-dev.txt` deliberately does not install them (that gigabyte
   is the point of the change); the note at the bottom of that file gives the
   command.

`tests/lib/jargon/test_onnx_embedding_parity.py` is the other thing that
wants torch, and it skips without it.

## Environment variables

| Variable | Needed for | Default |
| --- | --- | --- |
| `AWS_DEFAULT_REGION` | boto3 clients built at import time | none — collection fails without it |
| `EMBEDDING_MODEL_DIR` | where the exported ONNX model is read from | `lib/jargon/reader/assets/compiled/embedding_model`; the image sets it to `/home/worker/embedding_model` |
| `EMBEDDING_NUM_THREADS` | ONNX Runtime's thread budget for embedding | unset — one thread per core, as torch did |
| `BEDROCK_GLOBAL_ROUTING` | sends prio3 accounts' Claude calls to the `global.` profile, outside any residency (#2370) | `false` |
| `BEDROCK_EU_POOL_INCLUDE_EU_WEST_2` | adds eu-west-2 (London, not EU) back to the end of the EU Bedrock region pool (#2370) | `false` |
| `LABEL_PAGE_OCR_FALLBACK` | `1` lets a label sub-image the whole Textract ladder read nothing from take the page OCR's words inside its box (#2413); counted as `label_text_from_page_ocr` and `ocr.label.ladder{rung=page_ocr}`. Leave off until the words it supplies have been compared against a labelled sample of unread crops | unset (off) |
| `CALLBACK_HTTP_RETRY_ON_TIMEOUT` | retries a webhook POST that timed out, inside the 20s per-message budget and the request's own; `false` goes back to one attempt for a timeout, where the job stops and the owner is emailed. Read `callback.http.delivery` by `first_failure:timeout` for what it rescues (#2418) | `true` |
| `CALLBACK_REFUSE_PLAIN_HTTP` | refuses an `http://` webhook URL before anything is sent: the job stops and the owner is emailed to switch to https. Turn on only after reading `callback.http.scheme` (by `scheme`, `username`) for about two weeks and telling the accounts it names (#2405) | `false` |
| `CALLBACK_PLAIN_HTTP_ALLOWED_USERS` | comma-separated usernames still allowed `http://` while the refusal is on | empty |
| `LLM_REQUEST_SPEND_CEILING_USD` | per-request Bedrock spend past which the enrichment prompts (`enclosing_cuboid_vision`, `view_extent`) are skipped and the read records `llm_spend_ceiling`; tracked spend counts together with a fixed estimate reserved for each enrichment call still in flight ($0.01 per view_extent, $0.06 per cuboid read) (`lib/cost_tracking/spend_ceiling.py`, #2404); `0` turns it off | `1.50` |
| `EXTDIM_LAYOUT_GATE_SECONDS` | how long the cuboid read (the `enclosing_cuboid_vision` call) holds back for the layout call's verdict, since a rotational verdict discards it (`lib/techreader/external_dimensions/extractor`, #2424). Unset, it waits until the layout's LLM result-cache lookup has answered: a hit is the verdict, anything else starts the read at once, and never longer than 3s. Set to N, it is the fixed wait for the verdict it was before #2424: `10` restores the gate before #2375, `0` starts every cuboid read at once. Takes effect on a service update only (#2042) | unset |
| `INFERER_RESULT_BUS_ENABLED` | kill switch for the one-pub/sub-connection-per-loop inferer result bus (`lib/aredis/pubsub_bus.py`); `0` goes back to a connection per job | `1` |
| `INFERER_LEGACY_QUEUE_FALLBACK` | read an absent `crew-inferer:server:capabilities` key as a pre-v2 inferer and push to the legacy `crew-inferer:queue`; only for a fleet rolled back to an image that never advertises. Off, an absent key is waited for (up to 40s, clamped to the request budget) and then fails the job with `InfererUnavailable` | `0` |
| `CHARGE_LEDGER_REFUNDS_ENABLED` | writes whose fault a finished read was (`fault`, `fault_reason`) onto its `crew-api-request-log` row and refunds the charge when it was ours, including a read that answered but went out short (`read_incomplete`: it recorded a reason that becomes a `READ_INCOMPLETE` warning, refunded whole) (`lib/techreader/request/charge_ledger.py`, crew-api#213). The task role needs `dynamodb:UpdateItem` on `crew-api-request-log` (the verdict, and the row half of a refund; granted already, with `Query` on its indexes for rows from before crew-api#205) and `dynamodb:UpdateItem` on `crew-api-request-stats` (the refund's counters, infrastructure#277). A refund is a `TransactWriteItems`, which IAM authorises by each item's own action: there is no `dynamodb:TransactWriteItems` action, and no item is a `ConditionCheck`, so `ConditionCheckItem` is not needed. Enabled after crew-api's `CHARGE_LEDGER_ENABLED` | `0` |
| `WORKER_HEARTBEAT_ENABLED` | each worker's readiness heartbeat in Redis (`core-reader:worker:<task id>`, 15s TTL, rewritten every 5s and on each idle/busy change) and the once-a-minute fleet census that publishes `worker.fleet.idle` and `worker.fleet.busy` per tier (`lib/threads/worker_heartbeat.py`, infrastructure#283). Changes nothing about scaling or about which messages a worker takes; `0` turns off both, and `worker.first_poll.seconds` still reports | `1` |
| `READ_INCOMPLETE_WARNING_ENABLED` | puts one WARNING-level `READ_INCOMPLETE` exception on the COMPLETED message of a read that finished short, saying that it is incomplete and never why: no `reason`, no `ask_type`, because the degradation reasons describe our pipeline (the owner, on #2452; they stay in `request.read.degradation_count`) (`lib/techreader/request/read_incomplete.py`, werk24-python#586). Sent to Python clients reporting werk24 2.8.0 or newer, because every earlier release refuses a WARNING level and would fail the whole message, and to every request that reports no client version at all: the Python client always sends one, so that is a caller using the API directly, who gets the same warning (the owner, on #2451); `0` turns it off for everyone | `1` |
| `W24_AWS_REGION` | overrides the region for the service itself | falls back to `AWS_REGION`, then `AWS_DEFAULT_REGION`, then `eu-central-1` |
| `W24_ENVIRONMENT` | `dev` / `test` / `prod` | `dev` |
| `AWS_ACCOUNT_ID`, `S3_PREFIX` | the running service, not the unit tests | unset |
| `OPENCV_NUM_THREADS` | OpenCV's native thread budget | `1` |


## Did the merge to `prod` actually deploy?

Nothing in this repository deploys. There is no workflow for it, no buildspec
and no appspec: the image is built by CodeBuild *after* the merge, and the ECS
service picks it up on its own. So a merged pull request is not a deployed one,
and the gap has bitten before: prod served a six-hour-old image behind four
merged pull requests on 2026-09-01, because `requirements.txt` broke a build
nobody was watching.

**The release tag is the answer, and it is the `prod` commit SHA.** `Dockerfile`
takes `--build-arg W24_RELEASE=$(git rev-parse HEAD)` and exports it as both
`W24_RELEASE` and `SENTRY_RELEASE`, so every event the running image sends to
Sentry is stamped with the commit it was built from. Compare that against
`git rev-parse origin/prod` and there is no ambiguity.

`.claude/skills/monitoring/SKILL.md` has the Sentry coordinates, how to phrase
a query that works, and why a null is not a zero. Read it first; this section
is only the deploy question. There is no AWS CLI in an agent sandbox, so ECS
and CodeBuild cannot be asked directly, which is why this goes through Sentry
at all.

Group any dataset by `release` and compare the last-seen times:

```
dataset: metrics (or logs)
fields:  release, count(), max(timestamp_precise)
period:  24h
```

**Through the MCP connector that grouping does not construct.** Four phrasings
of it failed on 2026-09-17, on both `metrics` and `logs`, with the same "could
not construct a valid query" the monitoring skill describes for a grouping key
the emission does not carry. It works in the Metrics and Logs UI, where the
table above is still how to read it.

What answers the deploy question through the connector instead: **read the
`release` tag off an issue event.** Any issue from the window carries it
(`get_sentry_resource` on an issue shortId prints the tags), and it is the
running image's `W24_RELEASE`, so one issue is enough to say which commit
served the request that raised it. That is how the 2026-09-17 08:00 UTC release
was confirmed: `CORE-READER-179`'s events carried
`release: 910f03f1137e93041964881d516c5361ced6b8f0`, first seen 08:27:30 UTC
against a merge at 08:00:39 UTC. It answers "is the new SHA serving" but not
"has the old one stopped", so for a rollout still draining, use the UI.

Read the grouping like this:

| What you see | What it means |
| --- | --- |
| the new SHA reporting, the old one stopped | deployed, and the rollout finished |
| both reporting recently | rollout still draining; old tasks are still serving |
| only the old SHA, well after the merge | **not deployed**. Suspect the CodeBuild image build |
| the new SHA, nothing before it | first deploy of that service, or Sentry retention cut the rest |

Measured on the 2026-09-16 release (#2173): merged 17:23:40 UTC, first event on
the new SHA at 17:51:40, previous release last seen 17:07:21. **Allow about half
an hour** before treating silence as a failure.

Two things that read as a dead service and are not. `timestamp_precise` comes
back in **nanoseconds**, so divide by 1e9 before reading it as epoch seconds.
And a `period` shorter than the gap since the last event returns "No results
found", which looks identical to nothing running; widen to `24h` before
concluding anything. Liveness itself is a metrics question rather than a logs
one, for the reason the monitoring skill gives about `SENTRY_LOG_LEVEL`: one
recent `request.stage_seconds` or `request.document.*` sample is a request that
finished.


## Before you push

CI is a narrow check here. `.github/workflows/aws-sdk-pins.yml` reads three
pins out of `requirements.txt` and finishes in thirteen seconds; green means
the aiobotocore/boto3/botocore window is coherent. `.github/workflows/unit.yml`
(#2411) runs the offline suite in the `--ignore` shape below on the pull
request and again on its base, and fails only on an id that fails on the
change and not on the base (`tools/failing_ids.py`, with the wall-clock tests
in `tests/ci/quarantine.txt` reported but not gating). That is the diff this
file asks for, taken automatically; it says nothing about code no test
covers. Both runs share one venv unless the change moves `requirements.txt`,
`requirements.lock` or `requirements-dev.txt`; then the base runs on a venv
built from its own files, so a bump that breaks a test shows up as a new id
instead of breaking both sides alike. The validation is still yours: run
the tests that cover your change, and say in the pull request which command
you ran.

A baseline does not have to block your checkout. `git worktree add
/tmp/baseline origin/test` and run the suite there with the same interpreter
(`/path/to/repo/.venv/bin/python -m pytest ...`) — site-packages are absolute,
the repo modules come from the worktree, and you keep editing meanwhile. Add
`-p no:cacheprovider` so the two runs do not share a `.pytest_cache`, and
`git worktree remove` when done. Both runs must use the same installed
dependencies: a package present for one and not the other changes the
collection-error count with no code involved.

There used to be one asymmetry to expect here — the venv-inside-the-repo case
above, where a worktree baseline came out one lower than a baseline taken in
place. **It no longer applies**, because joblib left with scikit-learn and the
file that caused it is gone. Measured on 2026-09-20 across `55db744a` in a
worktree and #2245 in place: 127 failed both ways, with identical failing id
lists.

Do not correct for it. Subtracting an off-by-one that is not there is how a
real regression gets explained away. Compare the FAILED lists; a difference
that is real shows up as a named id, and this file's earlier entries measured
under the old behaviour are the ones to treat with care, not your run.
