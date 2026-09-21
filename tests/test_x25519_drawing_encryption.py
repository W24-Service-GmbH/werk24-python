"""The drawing can be encrypted to an X25519 key, not only an RSA one.

crew-api generates a fresh key pair on the INITIALIZE path for every
end-to-end request and sends the public half to the client, which encrypts the
drawing with it. RSA-2048 generation is a random prime search: measured at a
29.4ms median and a 92.7ms worst case of fifteen on a fast machine, several
times that on a Lambda vCPU, and with a right tail that is unbounded by
construction. X25519 is 0.028ms and has no tail (crew-api#146).

That is a wire-format change, so it is negotiated rather than switched: the
client declares what it can do, the server picks, and the KEY TYPE then tells
the recipient which format the package is in. Nothing carries a version flag.

These tests pin both formats and the declaration, because the failure mode of
getting it wrong is not an exception anyone sees quickly -- it is a customer's
drawing encrypted to a key nobody can use.
"""

import asyncio
import hashlib
import hmac
import json
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

from werk24.models.v2.internal import (
    KEY_EXCHANGE_RSA_OAEP,
    KEY_EXCHANGE_X25519,
    SUPPORTED_KEY_EXCHANGES,
    TechreadRequest,
)
from werk24.utils.crypt import (
    X25519_EPHEMERAL_KEY_BYTES,
    X25519_KDF_INFO,
    decrypt_with_private_key,
    derive_x25519_key,
    encrypt_with_public_key,
    generate_new_key_pair,
)

class _StopAfterSend(Exception):
    """Ends init_request once the command has been captured.

    The client would otherwise wait on a websocket that does not exist.
    """


PASSPHRASE = b"a-master-key"
DRAWING = b"%PDF-1.7\n" + b"a drawing" * 5000


def _x25519_pair(passphrase: bytes = PASSPHRASE):
    private_key = x25519.X25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


class TestTheX25519Format(unittest.TestCase):
    def test_a_drawing_survives_the_round_trip(self):
        private_pem, public_pem = _x25519_pair()
        package = encrypt_with_public_key(public_pem, DRAWING)
        self.assertEqual(
            decrypt_with_private_key(private_pem, PASSPHRASE, package), DRAWING
        )

    def test_the_package_opens_with_a_32_byte_ephemeral_key(self):
        """The layout the recipient parses: key block, IV, tag, ciphertext.

        core-reader reads this package as a STREAM and must know how many
        bytes to take before the IV, so the prefix length is part of the
        format rather than an implementation detail.
        """
        _, public_pem = _x25519_pair()
        package = encrypt_with_public_key(public_pem, DRAWING)
        overhead = len(package) - len(DRAWING)
        self.assertEqual(overhead, X25519_EPHEMERAL_KEY_BYTES + 12 + 16)

    def test_every_package_uses_a_fresh_ephemeral_key(self):
        """Reusing one would make the AES key the same for two drawings."""
        _, public_pem = _x25519_pair()
        first = encrypt_with_public_key(public_pem, DRAWING)
        second = encrypt_with_public_key(public_pem, DRAWING)
        self.assertNotEqual(
            first[:X25519_EPHEMERAL_KEY_BYTES], second[:X25519_EPHEMERAL_KEY_BYTES]
        )
        self.assertNotEqual(first, second)

    def test_another_key_cannot_open_it(self):
        private_pem, public_pem = _x25519_pair()
        other_private_pem, _ = _x25519_pair()
        package = encrypt_with_public_key(public_pem, DRAWING)
        with self.assertRaises(Exception):
            decrypt_with_private_key(other_private_pem, PASSPHRASE, package)

    def test_a_tampered_package_is_refused(self):
        """AES-GCM authenticates; a flipped byte must not decrypt."""
        private_pem, public_pem = _x25519_pair()
        package = bytearray(encrypt_with_public_key(public_pem, DRAWING))
        package[-1] ^= 0x01
        with self.assertRaises(Exception):
            decrypt_with_private_key(private_pem, PASSPHRASE, bytes(package))

    def test_the_derived_key_is_an_aes_256_key(self):
        self.assertEqual(len(derive_x25519_key(b"\x01" * 32)), 32)

    def test_the_derivation_matches_an_independent_hkdf(self):
        """Pinned against RFC 5869 worked by hand, not against itself.

        Calling `derive_x25519_key` twice and comparing proves only that it
        is a function. This is the wire-format contract with core-reader and
        with every drawing already encrypted under it: a changed hash, salt
        or `info` would silently make old packages undecryptable, and a
        self-comparison would pass through all three.

        So the expected value is computed here from `hmac` and `hashlib`
        alone -- HKDF-Extract then HKDF-Expand, RFC 5869 section 2 -- which
        shares no code with `cryptography`'s implementation.
        """
        secret = bytes(range(32))

        # HKDF-Extract: PRK = HMAC(salt, IKM), salt absent => HashLen zeros.
        prk = hmac.new(b"\x00" * hashlib.sha256().digest_size, secret, hashlib.sha256)
        # HKDF-Expand for one 32-byte block: T(1) = HMAC(PRK, info || 0x01).
        expected = hmac.new(
            prk.digest(), X25519_KDF_INFO + b"\x01", hashlib.sha256
        ).digest()

        self.assertEqual(derive_x25519_key(secret), expected)


class TestTheRsaFormatIsUntouched(unittest.TestCase):
    """Every account not yet on X25519 keeps working, unchanged."""

    def test_a_drawing_survives_the_round_trip(self):
        private_pem, public_pem = generate_new_key_pair(PASSPHRASE)
        package = encrypt_with_public_key(public_pem, DRAWING)
        self.assertEqual(
            decrypt_with_private_key(private_pem, PASSPHRASE, package), DRAWING
        )

    def test_the_package_still_opens_with_the_wrapped_aes_key(self):
        private_pem, public_pem = generate_new_key_pair(PASSPHRASE)
        package = encrypt_with_public_key(public_pem, DRAWING)
        overhead = len(package) - len(DRAWING)
        # RSA-2048: 256 bytes of wrapped key, then the same IV and tag.
        self.assertEqual(overhead, 256 + 12 + 16)


class TestTheCapabilityIsDeclaredNotAssumed(unittest.TestCase):
    def test_this_client_declares_both(self):
        self.assertEqual(
            SUPPORTED_KEY_EXCHANGES, [KEY_EXCHANGE_X25519, KEY_EXCHANGE_RSA_OAEP]
        )

    def test_a_request_from_an_older_client_declares_nothing(self):
        """The whole point of the empty default.

        The server parses THIS model out of the client's JSON. A default of
        `SUPPORTED_KEY_EXCHANGES` would make a request from a client too old
        to send the field claim support for everything in it, and the server
        would hand it a key it cannot use.
        """
        request = TechreadRequest.model_validate({"asks": [], "max_pages": 1})
        self.assertEqual(request.supported_key_exchanges, [])

    def test_this_client_sends_the_declaration(self):
        """The serialized command, not the source.

        Reading the source proves the keyword is written; it would still
        pass if the value were an empty list, or if the field failed to
        serialize. What the server acts on is the JSON, so assert on that.
        """
        from werk24 import techread

        client = techread.Werk24Client(token="t", region="r")
        sent = {}

        async def capture_command(action, message="{}"):
            sent["action"] = action
            sent["message"] = message
            raise _StopAfterSend()

        client._send_command = capture_command

        with self.assertRaises(_StopAfterSend):
            asyncio.run(client.init_request(asks=[], max_pages=1))

        payload = json.loads(sent["message"])
        self.assertEqual(
            payload["supported_key_exchanges"],
            [KEY_EXCHANGE_X25519, KEY_EXCHANGE_RSA_OAEP],
        )


if __name__ == "__main__":
    unittest.main()
