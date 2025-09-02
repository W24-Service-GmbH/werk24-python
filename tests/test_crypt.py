import io

import pytest

from werk24.utils.crypt import (
    decrypt_with_private_key,
    encrypt_with_public_key,
    generate_new_key_pair,
)


@pytest.fixture
def key_pair():
    """Generate a reusable RSA key pair for tests."""
    return generate_new_key_pair(b"super-secret")


def test_generate_new_key_pair_returns_pem(key_pair):
    private_key, public_key = key_pair
    assert private_key.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-")
    assert public_key.startswith(b"-----BEGIN PUBLIC KEY-")


def test_generate_new_key_pair_invalid_passphrase():
    with pytest.raises(RuntimeError):
        generate_new_key_pair("not-bytes")


def test_generate_new_key_pair_invalid_key_size():
    with pytest.raises(RuntimeError):
        generate_new_key_pair(b"pwd", key_size=1024)


def test_encrypt_decrypt_roundtrip_bytes(key_pair):
    private_key, public_key = key_pair
    data = b"hello cryptography"
    encrypted = encrypt_with_public_key(public_key, data)
    decrypted = decrypt_with_private_key(private_key, "super-secret", encrypted)
    assert decrypted == data


def test_encrypt_with_public_key_accepts_file_like(key_pair):
    _, public_key = key_pair
    buffer = io.BytesIO(b"file-like data")
    encrypted = encrypt_with_public_key(public_key, buffer)
    assert isinstance(encrypted, bytes)


def test_encrypt_with_public_key_invalid_data(key_pair):
    _, public_key = key_pair
    with pytest.raises(ValueError):
        encrypt_with_public_key(public_key, 123)  # type: ignore[arg-type]


def test_decrypt_with_private_key_incorrect_password(key_pair):
    private_key, public_key = key_pair
    encrypted = encrypt_with_public_key(public_key, b"secret")
    with pytest.raises(ValueError):
        decrypt_with_private_key(private_key, "wrong", encrypted)

