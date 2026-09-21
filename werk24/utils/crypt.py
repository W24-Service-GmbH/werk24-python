import io
import os
from typing import Optional, Tuple, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# the cryptography backend is stateless; creating it once avoids repeated
# initialisation cost in hot paths
BACKEND = default_backend()

#: Bytes an X25519 package carries in front of the IV: the sender's ephemeral
#: public key, raw-encoded. It plays the part RSA-OAEP's wrapped AES key plays
#: in the other format, and it is a fixed 32 rather than ``key_size // 8``.
X25519_EPHEMERAL_KEY_BYTES = 32

#: HKDF context for the AES key derived from an X25519 exchange.
#:
#: Binds the derived key to this protocol and this use. Two parties sharing a
#: secret for one purpose must not end up with the same AES key for another,
#: and an ``info`` string is what keeps that true without a second exchange.
#: Changing it is a wire-format break.
X25519_KDF_INFO = b"werk24-drawing-encryption-v1"


def derive_x25519_key(shared_secret: bytes) -> bytes:
    """The AES-256 key for an X25519 package, from the raw shared secret.

    HKDF rather than the raw X25519 output. The exchange returns a point with
    algebraic structure, and an AES key must be indistinguishable from
    uniformly random bytes; HKDF-SHA256 is what turns the first into the
    second. Both sides call this, so it is defined once.
    """
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=X25519_KDF_INFO,
        backend=BACKEND,
    ).derive(shared_secret)


def generate_new_key_pair(
    passphrase: bytes,
    public_exponent=65537,
    key_size=2048,
) -> Tuple[bytes, bytes]:
    """
    Generate a new RSA key pair and return the private and public key as PEM encoded bytes.

    Args:
    ----
    - passphrase (bytes): The passphrase to encrypt the private key with.
    - public_exponent (int): The public exponent to use for the key pair. Default is 65537.
    - key_size (int): The size of the key in bits. Default is 2048.

    Returns:
    -------
    tuple[bytes, bytes]: The private key and public key as PEM encoded bytes.
    """
    try:
        # Validate parameters
        if not isinstance(passphrase, bytes):
            raise ValueError("Passphrase must be of type 'bytes'.")
        if public_exponent <= 1 or public_exponent % 2 == 0:
            raise ValueError("Public exponent must be an odd integer greater than 1.")
        if key_size < 2048:
            raise ValueError("Key size must be at least 2048 bits for security.")

        # Generate the private key
        private_key = rsa.generate_private_key(
            public_exponent=public_exponent,
            key_size=key_size,
            backend=BACKEND,
        )

        # Serialize the private key with passphrase encryption
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(passphrase),
        )

        # Serialize the public key
        public_key = private_key.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_key_pem, public_key_pem

    except Exception as e:
        # Provide a generic error message for unexpected issues
        raise RuntimeError(f"Failed to generate RSA key pair: {e}") from e


def encrypt_with_public_key(
    public_key_pem: bytes,
    data: Union[bytes, io.BufferedReader],
) -> bytes:
    """
    Encrypt the data with the given public key.

    Args:
    ----
    - public_key_pem (bytes): The public key to use for encryption.
    - data (bytes): The data to encrypt.

    Returns:
    -------
    - bytes: The encrypted data.
    """

    # Ensure that the public key is in bytes
    if isinstance(public_key_pem, str):
        public_key_pem = public_key_pem.encode("utf-8")

    # Load the recipient's public key
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=BACKEND,
    )

    # ensure that the data is in bytes
    raw_data = data.read() if hasattr(data, "read") else data
    if not isinstance(raw_data, bytes):
        raise ValueError("Data must be bytes or a file-like object.")

    # The key type decides the format. Nothing else does, and nothing needs
    # to: the recipient loads its own private key before it reads a byte of
    # the package, so it already knows which prefix to expect. A version flag
    # in the payload would be a second source of truth for the same fact.
    if isinstance(public_key, x25519.X25519PublicKey):
        # ECIES. The AES key comes from an exchange with a throwaway key
        # pair, so nothing is wrapped and nothing is transmitted but the
        # ephemeral public half.
        ephemeral = x25519.X25519PrivateKey.generate()
        aes_key = derive_x25519_key(ephemeral.exchange(public_key))
        key_block = ephemeral.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    else:
        # RSA-OAEP key wrapping, the original format.
        aes_key = os.urandom(32)  # 256-bit AES key
        key_block = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    # Encrypt the file content with AES key in GCM mode
    iv = os.urandom(12)  # GCM standard IV size is 96 bits (12 bytes)

    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=BACKEND)
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(raw_data) + encryptor.finalize()

    # Combine the key block, IV, tag, and encrypted data. The layout is the
    # same for both formats; only the length of the first field differs.
    encrypted_package = key_block + iv + encryptor.tag + encrypted_data
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
    private_key_pem (bytes): The private key to use for decryption.
    passphrase (Optional[str]): The master key to decrypt the private key.
    encrypted_package (bytes): The encrypted package to decrypt.

    Returns:
    -------
    bytes: The decrypted data.
    """
    if isinstance(private_key_pem, str):
        private_key_pem = private_key_pem.encode("utf-8")

    if isinstance(password, str):
        password = password.encode("utf-8")

    # Load the recipient's private key
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=password,
        backend=BACKEND,
    )

    # The private key's own type says which format this package is in; see
    # encrypt_with_public_key.
    if isinstance(private_key, x25519.X25519PrivateKey):
        key_block_length = X25519_EPHEMERAL_KEY_BYTES
    else:
        key_block_length = private_key.key_size // 8

    # Extract the key block, IV, tag, and encrypted data
    key_block = encrypted_package[:key_block_length]
    iv = encrypted_package[key_block_length : key_block_length + 12]
    tag = encrypted_package[key_block_length + 12 : key_block_length + 28]
    encrypted_data = encrypted_package[key_block_length + 28 :]

    if isinstance(private_key, x25519.X25519PrivateKey):
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(key_block)
        aes_key = derive_x25519_key(private_key.exchange(peer_public_key))
    else:
        # Decrypt the AES key with the recipient's RSA private key
        aes_key = private_key.decrypt(
            key_block,
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
        backend=BACKEND,
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    return decrypted_data
