from test.utils import AsyncTestCase

from werk24._version import __version__
from werk24.techread_client import W24TechreadClient

from .utils import get_drawing, get_model


class TestCrypt(AsyncTestCase):

    def test_generate_new_key_pair(self) -> None:
        """Test whether we can generate a new key pair.

        User Story: As API user, I want to generate a new key pair,
        so that I can encrypt and decrypt data.
        """
        public_key, private_key = W24TechreadClient.generate_encryption_keys(
            b"passphrase"
        )
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_encrypt_decrypt_loop(self) -> None:
        """Test whether we can encrypt and decrypt data.

        User Story: As API user, I want to encrypt and decrypt data,
        so that I can securely transmit data.
        """
        public_key_pem, private_key_pem = W24TechreadClient.generate_encryption_keys(
            b"passphrase"
        )
        data = b"Hello, World!"
        encrypted = W24TechreadClient.encrypt_with_public_key(public_key_pem, data)
        decrypted = W24TechreadClient.decrypt_with_private_key(
            private_key_pem, b"passphrase", encrypted
        )
        self.assertEqual(data, decrypted)
