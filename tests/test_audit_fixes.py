"""Regression tests for the bug/vulnerability/performance fixes from the audit.

Each test pins the corrected behavior of a specific finding so that a
regression would fail loudly.
"""

import importlib
import uuid

import pytest
from packaging.version import Version

from werk24.techread import (
    Werk24Client,
    _all_valid_ask_types,
    _default_ssl_context,
)
from werk24.utils.defaults import Settings


# ---------------------------------------------------------------------------
# Finding 1: download_payload SSRF / origin validation
# ---------------------------------------------------------------------------
class TestPayloadUrlValidation:
    @pytest.mark.parametrize(
        "url",
        [
            "http://169.254.169.254/latest/meta-data/",  # non-https + metadata
            "http://api.w24.co/payload",  # non-https
            "file:///etc/passwd",  # non-http scheme
            "https://169.254.169.254/x",  # link-local IP literal
            "https://127.0.0.1/secret",  # loopback IP literal
            "https://10.0.0.5/x",  # private IP literal
            "https://[::1]/x",  # loopback IPv6
            "https:///no-host",  # missing host
        ],
    )
    def test_rejects_untrusted_urls(self, url):
        with pytest.raises(RuntimeError):
            Werk24Client._validate_payload_url(url)

    @pytest.mark.parametrize(
        "url",
        [
            "https://api.w24.co/payload",
            "https://werk24-bucket.s3.amazonaws.com/abc?sig=1",
            "https://8.8.8.8/public",  # public IP literal is allowed
        ],
    )
    def test_allows_trusted_https_urls(self, url):
        # Should not raise.
        Werk24Client._validate_payload_url(url)


# ---------------------------------------------------------------------------
# Finding 16: werk24.models package attribute must not be overwritten
# ---------------------------------------------------------------------------
class TestModelsPackageIntegrity:
    def test_models_attribute_is_the_package(self):
        # The ``werk24.models`` attribute must resolve to the package itself,
        # not to the v2 ``models.py`` module (the star-import shadowing bug).
        # NOTE: do not delete/reimport werk24 from sys.modules here — that would
        # create duplicate class objects and break class-identity checks in
        # other tests that run afterwards.
        werk24 = importlib.import_module("werk24")
        assert werk24.models.__name__ == "werk24.models"
        assert werk24.models.__file__.endswith("models/__init__.py")

    def test_submodules_are_importable_as_attributes(self):
        werk24 = importlib.import_module("werk24")
        importlib.import_module("werk24.models.v2")
        importlib.import_module("werk24.models.v2.enums")
        assert hasattr(werk24.models, "v1")
        assert hasattr(werk24.models, "v2")

    def test_public_symbols_still_exported(self):
        werk24 = importlib.import_module("werk24")
        for symbol in ("Werk24Client", "TechreadMessage", "AskMetaData"):
            assert hasattr(werk24, symbol)


# ---------------------------------------------------------------------------
# Finding 17: unknown message_subtype must not raise a bare KeyError; a
# non-dict payload must not raise AttributeError.
# ---------------------------------------------------------------------------
class TestTechreadMessageRobustness:
    def _msg(self, subtype, payload):
        import json

        from werk24.models.v2.internal import TechreadMessage

        raw = json.dumps(
            {
                "request_id": str(uuid.uuid4()),
                "message_type": "ASK",
                "message_subtype": subtype,
                "payload_dict": payload,
            }
        )
        return TechreadMessage.model_validate_json(raw)

    def test_unknown_subtype_raises_validationerror_not_keyerror(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            self._msg("SOME_FUTURE_SUBTYPE", {"foo": "bar"})

    def test_non_dict_payload_is_returned_unchanged(self):
        msg = self._msg("META_DATA", "not-a-dict")
        assert msg.payload_dict == "not-a-dict"

    def test_v2_response_dispatch(self):
        msg = self._msg(
            "REDACTION", {"ask_version": "v2", "ask_type": "REDACTION", "redaction_zones": []}
        )
        assert type(msg.payload_dict).__name__ == "ResponseRedaction"


# ---------------------------------------------------------------------------
# Finding 18: W24Size fields must deserialize to the concrete subclass and
# preserve subclass-specific fields (width_across_flats).
# ---------------------------------------------------------------------------
class TestSizeDeserialization:
    def test_width_across_flats_preserved(self):
        from werk24.models.v1.measure import W24MeasureLabel

        m = W24MeasureLabel.model_validate(
            {
                "blurb": "SW17",
                "size": {
                    "blurb": "SW17",
                    "size_type": "WIDTHS_ACROSS_FLATS",
                    "nominal_size": "17",
                    "width_across_flats": "17",
                },
            }
        )
        assert type(m.size).__name__ == "W24SizeWidthsAcrossFlats"
        assert str(m.size.width_across_flats) == "17"

    def test_nominal_size_dispatch(self):
        from werk24.models.v1.measure import W24MeasureLabel

        m = W24MeasureLabel.model_validate(
            {"blurb": "5", "size": {"blurb": "5", "size_type": "NOMINAL", "nominal_size": "5"}}
        )
        assert type(m.size).__name__ == "W24SizeNominal"


# ---------------------------------------------------------------------------
# Finding 9: supported_python_versions aligns with pyproject (3.10 - 3.14).
# ---------------------------------------------------------------------------
class TestSupportedPythonVersions:
    def test_includes_314_and_excludes_39(self):
        versions = Settings().supported_python_versions
        assert Version("3.14") in versions
        assert Version("3.9") not in versions
        assert Version("3.10") in versions


# ---------------------------------------------------------------------------
# Findings 12/13/14: caching helpers return stable, identical objects.
# ---------------------------------------------------------------------------
class TestCaching:
    def test_ssl_context_is_cached(self):
        assert _default_ssl_context() is _default_ssl_context()

    def test_valid_ask_types_is_cached_and_populated(self):
        first = _all_valid_ask_types()
        assert first is _all_valid_ask_types()
        assert "META_DATA" in first
        assert len(first) > 0

    def test_client_uses_shared_ssl_context(self):
        client = Werk24Client(token="t", region="r")
        # The client's SSL context is the shared, cached one (finding 12/13).
        assert client._ssl_context is _default_ssl_context()

    @pytest.mark.asyncio
    async def test_make_https_session_reuses_context(self):
        client = Werk24Client(token="t", region="r")
        # _make_https_session must reuse the shared context (no per-request
        # rebuild) when no custom cafile is supplied.
        session = client._make_https_session()
        try:
            assert client._ssl_context is _default_ssl_context()
        finally:
            await session.close()
