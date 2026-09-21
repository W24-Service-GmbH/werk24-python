"""What a correct Werk24 callback looks like, in one place.

The rules here are the ones the server actually commits to, read off the
delivery path in core-reader (``lib/techreader_helper/callback/callback_proxy.py``)
rather than off the documentation:

- The body is ``TechreadMessage.model_dump_json()`` and nothing else, so a
  client's ``TechreadMessage.model_validate_json`` must accept it verbatim.
- ``Content-Type`` is ``application/json`` and ``User-Agent`` is
  ``Werk24-Callback-Worker``, both set explicitly by the sender.
- The customer's own ``callback_headers`` are forwarded; only transport and
  hop-by-hop headers are stripped.
- Every message of one request carries that request's id.
- A read is bookended: ``PROGRESS/STARTED`` first, ``PROGRESS/COMPLETED`` last,
  with one ``ASK`` message per requested ask in between.

Checked separately from the transport, and all at once rather than one
assertion at a time, because a callback check that costs a billable read
should report everything that was wrong with the batch it paid for.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Sequence
from uuid import UUID

from pydantic import ValidationError

from werk24 import TechreadMessage, TechreadMessageSubtype, TechreadMessageType
from werk24.models.v2.asks import AskType, AskUnion
from werk24.models.v2.responses import Response

from tests.callback_check.receiver import CallbackDelivery

__all__ = ["CallbackContractError", "assert_callback_contract"]

EXPECTED_CONTENT_TYPE = "application/json"
EXPECTED_USER_AGENT = "Werk24-Callback-Worker"


class CallbackContractError(AssertionError):
    """Raised when delivered callbacks violate the contract.

    An ``AssertionError`` so pytest renders it as a plain test failure, with
    every violation listed rather than only the first.
    """

    def __init__(self, problems: Sequence[str]) -> None:
        self.problems = list(problems)
        body = "\n".join(f"  - {problem}" for problem in self.problems)
        super().__init__(
            f"{len(self.problems)} callback contract violation(s):\n{body}"
        )


def _reject_non_json_constant(token: str) -> Any:
    """Refuse the tokens ``NaN``, ``Infinity`` and ``-Infinity``.

    None of the three is JSON, and strict receivers reject them. The sender
    serialises with pydantic specifically so they cannot appear -- pydantic
    writes ``null`` for a non-finite float where the stdlib encoder would emit
    a bare token -- which makes this the check that would notice if the body
    ever went back through a different writer.

    A genuine infinity in this API ("R PLANE" is a radius of infinity) is
    carried as a ``Decimal`` and serialises to the JSON *string* ``"Infinity"``,
    which never reaches this hook.
    """
    raise ValueError(f"body contains the non-JSON constant {token!r}")


def _subtype_value(subtype: Any) -> str:
    """The wire value of a message subtype, whichever enum it resolved to."""
    return str(getattr(subtype, "value", subtype))


def _check_transport(
    delivery: CallbackDelivery,
    expected_path: str,
    expected_headers: Mapping[str, str],
    problems: List[str],
    label: str,
) -> None:
    if delivery.method != "POST":
        problems.append(f"{label}: method is {delivery.method}, expected POST")

    if delivery.path != expected_path:
        problems.append(
            f"{label}: posted to {delivery.path!r}, expected {expected_path!r}"
        )

    # Compared on the media type alone: a charset parameter would be correct
    # here and is not something to fail a release over.
    content_type = delivery.headers.get("content-type", "")
    if content_type.split(";")[0].strip().lower() != EXPECTED_CONTENT_TYPE:
        problems.append(
            f"{label}: Content-Type is {content_type!r}, "
            f"expected {EXPECTED_CONTENT_TYPE!r}"
        )

    user_agent = delivery.headers.get("user-agent")
    if user_agent != EXPECTED_USER_AGENT:
        problems.append(
            f"{label}: User-Agent is {user_agent!r}, expected {EXPECTED_USER_AGENT!r}"
        )

    for name, value in expected_headers.items():
        actual = delivery.headers.get(name.lower())
        if actual != value:
            problems.append(
                f"{label}: callback header {name!r} arrived as {actual!r}, "
                f"expected {value!r}"
            )


def _parse_body(
    delivery: CallbackDelivery,
    problems: List[str],
    label: str,
) -> TechreadMessage | None:
    try:
        text = delivery.body.decode("utf-8")
    except UnicodeDecodeError as exception:
        problems.append(f"{label}: body is not valid UTF-8 ({exception})")
        return None

    # Parsed twice on purpose, and the two passes answer different questions.
    # json.loads says whether the bytes are JSON at all -- with the non-finite
    # tokens refused, which pydantic's parser accepts. TechreadMessage says
    # whether they are a message this client can read.
    try:
        json.loads(text, parse_constant=_reject_non_json_constant)
    except ValueError as exception:
        problems.append(f"{label}: {exception}")
        return None

    try:
        return TechreadMessage.model_validate_json(text)
    except ValidationError as exception:
        problems.append(
            f"{label}: body does not validate as TechreadMessage: "
            f"{exception.error_count()} error(s), first at "
            f"{exception.errors()[0].get('loc')}: "
            f"{exception.errors()[0].get('msg')}"
        )
        return None


def _check_sequence(
    messages: Sequence[TechreadMessage],
    request_id: UUID,
    asks: Sequence[AskUnion],
    problems: List[str],
) -> None:
    for index, message in enumerate(messages):
        if message.request_id != request_id:
            problems.append(
                f"message {index} carries request_id {message.request_id}, "
                f"expected {request_id}"
            )

    subtypes = [m.message_subtype for m in messages]

    if TechreadMessageSubtype.PROGRESS_STARTED not in subtypes:
        problems.append("no PROGRESS/STARTED message was delivered")
    elif subtypes[0] != TechreadMessageSubtype.PROGRESS_STARTED:
        # Position, not just presence. core-reader joins the STARTED task at
        # the top of every schedule_callback precisely so nothing overtakes it,
        # so an ASK that arrives first is a real ordering defect -- and a
        # customer keying off STARTED to open a record would miss it.
        problems.append(
            "PROGRESS/STARTED was not the first message delivered "
            f"(first was {subtypes[0]})"
        )

    if TechreadMessageSubtype.PROGRESS_COMPLETED not in subtypes:
        problems.append("no PROGRESS/COMPLETED message was delivered")
    elif subtypes[-1] != TechreadMessageSubtype.PROGRESS_COMPLETED:
        problems.append(
            "PROGRESS/COMPLETED was not the last message delivered "
            f"(last was {subtypes[-1]})"
        )

    for index, message in enumerate(messages):
        if message.message_type == TechreadMessageType.ERROR:
            problems.append(
                f"message {index} is an ERROR ({message.message_subtype}), "
                f"exceptions={message.exceptions}"
            )

    _check_ask_messages(messages, asks, problems)


def _check_ask_messages(
    messages: Sequence[TechreadMessage],
    asks: Sequence[AskUnion],
    problems: List[str],
) -> None:
    """One well-formed ASK message per requested ask, and no others.

    The payload check is the point of the whole exercise: a message that
    validates as a ``TechreadMessage`` but whose ``payload_dict`` came back as
    a plain dict means ``TechreadMessage.deserialize_payload`` found no
    response model that matched -- the server and the client have drifted, and
    every customer reading ``payload_dict.<field>`` is broken. That failure is
    invisible to a shape check on the envelope alone.
    """
    ask_messages = [m for m in messages if m.message_type == TechreadMessageType.ASK]

    # Keyed by the enum's *value*. ``message_subtype`` is a union that can
    # resolve to either the v2 ``AskType`` or the v1 ``W24AskType``, and the
    # two are distinct enum classes carrying the same members. Comparing the
    # strings sidesteps the question of which one a given payload produced.
    delivered: Dict[str, List[TechreadMessage]] = {}
    for message in ask_messages:
        delivered.setdefault(_subtype_value(message.message_subtype), []).append(
            message
        )

    requested = {ask.ask_type.value: ask.ask_type for ask in asks}

    for value, ask_type in requested.items():
        matching = delivered.get(value, [])
        if not matching:
            problems.append(f"no ASK message was delivered for {ask_type}")
            continue
        if len(matching) > 1:
            problems.append(
                f"{len(matching)} ASK messages were delivered for {ask_type}, "
                "expected 1"
            )

        for message in matching:
            _check_ask_payload(message, ask_type, problems)

    for value, matching in delivered.items():
        if value not in requested:
            problems.append(
                f"{len(matching)} ASK message(s) delivered for {value}, "
                "which was never requested"
            )


def _check_ask_payload(
    message: TechreadMessage,
    ask_type: AskType,
    problems: List[str],
) -> None:
    label = f"ASK/{ask_type.value}"

    if message.exceptions:
        problems.append(f"{label}: carries exceptions {message.exceptions}")

    payload = message.payload_dict
    if payload is None:
        # Only a message with a binary deliverable may omit the dict.
        if message.payload_url is None:
            problems.append(f"{label}: has neither payload_dict nor payload_url")
        return

    # The v2 ``Response`` deliberately, not every family
    # ``deserialize_payload`` can return. ``asks`` is typed ``Sequence[AskUnion]``
    # and the v1 and v2 ask-type names do not overlap, so a v1 payload can only
    # ever arrive under a subtype that was never requested -- which the caller
    # above already reports as such. Widening this to the v1 classes would not
    # reach that case and would cost real strictness here: those classes carry
    # no ``ask_type``, so a v1 payload delivered under a v2 ask would pass both
    # this check and the discriminator check below, silently.
    if not isinstance(payload, Response):
        problems.append(
            f"{label}: payload_dict did not deserialize into a response model "
            f"(got {type(payload).__name__}). The client has no model matching "
            "what the server sent."
        )
        return

    if payload.ask_type != ask_type:
        problems.append(
            f"{label}: payload is a {payload.ask_type} response, expected {ask_type}"
        )


def assert_callback_contract(
    deliveries: Sequence[CallbackDelivery],
    request_id: UUID,
    asks: Sequence[AskUnion],
    expected_path: str,
    expected_headers: Mapping[str, str] | None = None,
) -> List[TechreadMessage]:
    """Check every recorded delivery against the callback contract.

    Args:
    ----
    - deliveries: What the receiver recorded, in arrival order.
    - request_id (UUID): The id the API returned for the submission.
    - asks: The asks that were requested.
    - expected_path (str): The path the callbacks were registered on.
    - expected_headers: The ``callback_headers`` that were registered. Each
      must come back verbatim.

    Returns:
    -------
    - List[TechreadMessage]: The parsed messages, in arrival order.

    Raises:
    ------
    - CallbackContractError: Listing every violation found, not just the first.
    """
    problems: List[str] = []
    expected_headers = expected_headers or {}

    if not deliveries:
        raise CallbackContractError(
            [
                "no callback was delivered at all. The request was accepted "
                f"as {request_id}, so either the read never completed or the "
                "callback was not sent."
            ]
        )

    messages: List[TechreadMessage] = []
    for index, delivery in enumerate(deliveries):
        label = f"delivery {index}"
        _check_transport(delivery, expected_path, expected_headers, problems, label)
        message = _parse_body(delivery, problems, label)
        if message is not None:
            messages.append(message)

    # Only when every body parsed. Judging the sequence off a partial list
    # would add "no PROGRESS/COMPLETED was delivered" on top of the parse
    # failure that swallowed it, which buries the real problem.
    if len(messages) == len(deliveries):
        _check_sequence(messages, request_id, asks, problems)

    if problems:
        raise CallbackContractError(problems)

    return messages
