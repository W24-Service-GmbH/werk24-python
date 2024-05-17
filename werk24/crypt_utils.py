from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from typing import Tuple


def generate_new_key_pair(
    passphrase: bytes,
    public_exponent=65537,
    key_size=2048,
) -> Tuple[bytes, bytes]:
    """
    Generate a new RSA key pair and return the private and public key as PEM encoded bytes.

    Args:
    ----
    passphrase: bytes
        The passphrase to encrypt the private key with.

    public_exponent: int
        The public exponent to use for the key pair. Default is 65537.

    key_size: int
        The size of the key in bits. Default is 2048.

    Returns:
    -------
    tuple[bytes, bytes]
        The private key and public key as PEM encoded bytes.
    """
    if isinstance(passphrase, str):
        passphrase = passphrase.encode("utf-8")

    private_key = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
        backend=default_backend(),
    )

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
    )

    public_key = private_key.public_key()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key_pem, public_key_pem


def encrypt_with_public_key(public_key: bytes, data: bytes) -> bytes:
    """
    Encrypt the data with the given public key.

    Args:
    ----
    public_key: bytes
        The public key to use for encryption.

    data: bytes
        The data to encrypt.

    Returns:
    -------
    bytes
        The encrypted data.
    """
    public_key = serialization.load_pem_public_key(
        public_key,
        backend=default_backend(),
    )
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
