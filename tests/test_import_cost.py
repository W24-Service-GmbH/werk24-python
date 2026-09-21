"""What ``import werk24`` is allowed to cost.

Five repositories install this package from main, and three of the consumers
that matter most never construct a client: crew-api's ``handler_read``,
``handler_initialize`` and ``handler_read_with_callback`` import werk24 only
to validate a payload. They are Lambdas, so the import is paid on every cold
start, in front of a customer request, on the WebSocket and callback submit
paths.

``werk24.techread`` was imported eagerly by ``werk24/__init__.py``, so every
one of those cold starts built the websocket client and aiohttp under it.
Measured on python 3.13 with the pinned requirements, three runs each:

    import werk24    784ms  ->  608ms

The rest is pydantic building the models, which a consumer that imports a
model does need.

These tests run in a subprocess on purpose. ``sys.modules`` in the test
process already holds aiohttp and ``werk24.techread`` -- the client tests
import them -- so an in-process check would pass no matter what
``werk24/__init__.py`` did.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(code: str) -> subprocess.CompletedProcess:
    """Run a snippet in a fresh interpreter rooted at the repository.

    Args:
        code (str): Python source to execute.

    Returns:
        subprocess.CompletedProcess: The finished process, stdout captured.
    """
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _modules_after(statement: str) -> set:
    """Top-level module names loaded after running one import statement.

    Args:
        statement (str): The import statement under test.

    Returns:
        set: Every top-level package name in ``sys.modules`` afterwards.
    """
    result = _run(
        "import sys, json\n"
        f"{statement}\n"
        "print(json.dumps(sorted({m.split('.')[0] for m in sys.modules})))\n"
    )
    assert result.returncode == 0, result.stderr
    return set(json.loads(result.stdout.strip().splitlines()[-1]))


class TestTheClientIsNotImportedUntilItIsAsked:
    """``import werk24`` must not drag the websocket client in with it."""

    def test_a_plain_import_does_not_load_aiohttp(self):
        """aiohttp is the expensive half of ``werk24.techread``.

        Asserted on aiohttp rather than on ``werk24.techread`` because it is
        the cost, not the name: 118ms of the 183ms. A refactor that moved the
        client somewhere else but still imported aiohttp eagerly would be the
        same regression under a different module name.
        """
        loaded = _modules_after("import werk24")
        assert "aiohttp" not in loaded
        assert "werk24" in loaded

    def test_a_plain_import_does_not_load_the_techread_module(self):
        loaded = _modules_after(
            "import werk24, sys\n"
            "assert 'werk24.techread' not in sys.modules, 'techread was imported'"
        )
        assert "werk24" in loaded

    def test_importing_a_model_does_not_load_the_client(self):
        """The crew-api case, spelled the way those handlers spell it."""
        loaded = _modules_after(
            "from werk24 import TechreadWithCallbackPayload  # noqa: F401"
        )
        assert "aiohttp" not in loaded

    @pytest.mark.parametrize(
        "statement",
        [
            "from werk24 import Werk24Client",
            "import werk24; werk24.Werk24Client",
            "import werk24; werk24.techread.Werk24Client",
            "import werk24.techread; werk24.techread.Werk24Client",
            "from werk24.techread import Werk24Client",
        ],
        ids=[
            "from-werk24-import",
            "attribute-on-package",
            "submodule-attribute",
            "explicit-submodule-import",
            "direct-from-submodule",
        ],
    )
    def test_every_spelling_still_reaches_the_client(self, statement):
        """Each of these worked before the client went lazy; each must still.

        ``werk24.techread`` as an attribute is the one that is easy to lose:
        it was bound only because ``__init__`` imported it, so dropping that
        import turns it into an ``AttributeError`` unless the package resolves
        the submodule itself.
        """
        # The statement is the assertion: every spelling ends by touching
        # Werk24Client, so a lost name raises AttributeError or ImportError
        # and the subprocess exits non-zero.
        result = _run(statement)
        assert result.returncode == 0, result.stderr


class TestThePublicSurfaceIsUnchanged:
    """Going lazy must not quietly remove a name people import."""

    def test_star_import_still_exports_the_client(self):
        """A lazy attribute survives ``import *`` only if ``__all__`` lists it.

        Without ``__all__``, ``from werk24 import *`` copies what is already
        in ``globals()`` -- and ``Werk24Client`` is deliberately not there.
        """
        result = _run(
            "ns = {}\n"
            "exec('from werk24 import *', ns)\n"
            "assert 'Werk24Client' in ns, 'star import lost Werk24Client'\n"
            "assert ns['Werk24Client'].__name__ == 'Werk24Client'\n"
        )
        assert result.returncode == 0, result.stderr

    def test_star_import_still_exports_the_models(self):
        """A spot check across models, exceptions and helpers."""
        result = _run(
            "ns = {}\n"
            "exec('from werk24 import *', ns)\n"
            "for name in ('AskUnion', 'TechreadMessage', 'TechreadWithCallbackPayload',\n"
            "             'Material', 'W24Ask', 'BadRequestException',\n"
            "             'get_test_drawing', 'deserialize_ask_response'):\n"
            "    assert name in ns, name\n"
        )
        assert result.returncode == 0, result.stderr

    def test_star_import_exports_no_module_objects(self):
        """``__all__`` must not re-export submodules.

        Importing a submodule binds it on its parent package, so ``models``
        and ``utils`` are in this package's globals. Re-exporting them lets a
        star import shadow the real packages in the caller's namespace --
        which is the trap ``werk24.models`` already documents in its own
        ``__all__``.
        """
        result = _run(
            "import types\n"
            "ns = {}\n"
            "exec('from werk24 import *', ns)\n"
            "leaked = sorted(n for n, v in ns.items() if isinstance(v, types.ModuleType))\n"
            "assert not leaked, leaked\n"
        )
        assert result.returncode == 0, result.stderr

    def test_version_is_still_available(self):
        result = _run("import werk24; assert werk24.__version__.count('.') >= 1")
        assert result.returncode == 0, result.stderr

    def test_an_unknown_attribute_raises_attribute_error(self):
        """Not ``ImportError``.

        ``hasattr``, ``copy`` and ``pickle`` all probe modules for dunder
        names they do not have; a ``__getattr__`` that raised anything else
        would break them far from here.
        """
        result = _run(
            "import werk24\n"
            "try:\n"
            "    werk24.NoSuchName\n"
            "except AttributeError:\n"
            "    pass\n"
            "else:\n"
            "    raise SystemExit('expected AttributeError')\n"
        )
        assert result.returncode == 0, result.stderr

    def test_dir_lists_the_lazy_name(self):
        """Tab completion and ``dir()`` should not lose it."""
        result = _run("import werk24; assert 'Werk24Client' in dir(werk24)")
        assert result.returncode == 0, result.stderr

    def test_dir_lists_the_lazy_submodule_before_it_is_touched(self):
        """``dir(werk24)`` listed ``techread`` on main, so it must here too.

        The "before it is touched" is the whole test: resolving the
        attribute puts it in ``globals()``, after which any ``__dir__``
        reports it. The regression is only visible on a plain ``import
        werk24``, which is also the only moment tab completion matters.
        """
        result = _run(
            "import werk24\n"
            "assert 'techread' in dir(werk24), 'dir() lost the techread submodule'\n"
            "import sys\n"
            "assert 'werk24.techread' not in sys.modules, 'dir() imported it'\n"
        )
        assert result.returncode == 0, result.stderr

    def test_dir_does_not_promise_a_name_that_does_not_resolve(self):
        """Everything ``dir()`` advertises must actually be gettable."""
        result = _run(
            "import werk24\n"
            "for name in dir(werk24):\n"
            "    getattr(werk24, name)\n"
        )
        assert result.returncode == 0, result.stderr
