"""Harness for checking that Werk24 callbacks are actually delivered, and correct.

The pieces are deliberately separate from the assertions in
``tests/test_callback_e2e.py``:

- :mod:`tests.callback_check.receiver` is a local HTTP server that records what
  arrives, and nothing else. It makes no judgement about the payload.
- :mod:`tests.callback_check.tunnel` gives that server a public HTTPS URL, so
  the production API can reach it from a CI runner that has no inbound address.
- :mod:`tests.callback_check.contract` holds what "correct" means, so the rules
  can be read in one place and reused against a recorded delivery without
  spending a read.
"""

from tests.callback_check.contract import (
    CallbackContractError,
    assert_callback_contract,
)
from tests.callback_check.receiver import CallbackDelivery, CallbackReceiver
from tests.callback_check.tunnel import (
    QuickTunnel,
    TunnelUnavailable,
    cloudflared_binary,
)

__all__ = [
    "CallbackContractError",
    "CallbackDelivery",
    "CallbackReceiver",
    "QuickTunnel",
    "TunnelUnavailable",
    "assert_callback_contract",
    "cloudflared_binary",
]
