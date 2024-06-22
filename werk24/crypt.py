import os
import io
from typing import Optional, Union
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
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

    return public_key_pem, private_key_pem


def encrypt_with_public_key(
    public_key_pem: bytes,
    data: Union[bytes, io.BufferedReader],
) -> bytes:
    """
    Encrypt the data with the given public key.

    Args:
    ----
    public_key_pem: bytes
        The public key to use for encryption.

    data: bytes
        The data to encrypt.

    Returns:
    -------
    bytes
        The encrypted data.
    """

    # Ensure that the public key is in bytes
    if isinstance(public_key_pem, str):
        public_key_pem = public_key_pem.encode("utf-8")

    # Load the recipient's public key
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend(),
    )

    # ensure that the data is in bytes
    if hasattr(data, "read"):
        raw_data = data.read()
    else:
        raw_data = data

    # Encrypt the file content with AES key in GCM mode
    aes_key = os.urandom(32)  # 256-bit AES key
    iv = os.urandom(12)  # GCM standard IV size is 96 bits (12 bytes)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(raw_data) + encryptor.finalize()

    # Encrypt the AES key with the recipient's RSA public key
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Combine the encrypted AES key, IV, tag, and encrypted data
    encrypted_package = encrypted_aes_key + iv + encryptor.tag + encrypted_data
    return encrypted_package


def decrypt_with_private_key(
    private_key_pem: bytes,
    password: Optional[str],
    encrypted_package: bytes,
) -> bytes:
    """
    Decrypt the encrypted package with the given private key.

    Args:
    ----
    private_key_pem: bytes
        The private key to use for decryption.

    passphrase: str | None
        The master key to decrypt the private key.

    encrypted_package: bytes
        The encrypted package to decrypt.

    Returns:
    -------
    bytes
        The decrypted data.
    """
    if isinstance(private_key_pem, str):
        private_key_pem = private_key_pem.encode("utf-8")

    if isinstance(password, str):
        password = password.encode("utf-8")

    # Load the recipient's private key
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=password,
        backend=default_backend(),
    )

    # Extract the encrypted AES key, IV, tag, and encrypted data
    encrypted_aes_key = encrypted_package[: private_key.key_size // 8]
    iv = encrypted_package[private_key.key_size // 8 : private_key.key_size // 8 + 12]
    tag = encrypted_package[
        private_key.key_size // 8 + 12 : private_key.key_size // 8 + 28
    ]
    encrypted_data = encrypted_package[private_key.key_size // 8 + 28 :]

    # Decrypt the AES key with the recipient's RSA private key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Decrypt the file content with the decrypted AES key in GCM mode
    cipher = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv, tag),
        backend=default_backend(),
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    return decrypted_data
