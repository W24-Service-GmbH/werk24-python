"""Root pytest configuration for the werk24 test suite."""

# No pytest_plugins needed - fixtures are imported directly where needed

import pytest


@pytest.fixture(autouse=True)
def _keep_the_real_home_license_file(tmp_path_factory, monkeypatch):
    """Point ``werk24 init``'s save path at a temporary folder in every test.

    ``werk24 init`` saves the key to ``USER_LICENSE_PATH`` (``~/.werk24``).
    Without this, a test that runs it would overwrite the developer's or the
    CI runner's real key.
    """
    import werk24.utils.license as license_module

    home = tmp_path_factory.mktemp("home")
    monkeypatch.setattr(license_module, "USER_LICENSE_PATH", str(home / ".werk24"))
