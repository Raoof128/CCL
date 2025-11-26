"""Mock Key Management Service for educational use.

Implements deterministic key derivation and authenticated wrapping using
standard library primitives. No real secrets should be persisted.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Dict


class KMSMock:
    """Lightweight KMS-style helper.

    The mock uses PBKDF2 for key derivation and a simple XOR stream cipher for
    payload confidentiality. A HMAC provides integrity to avoid silent
    corruption. This design is intentionally transparent and educational
    rather than production hardened.
    """

    def __init__(self, master_secret: bytes | None = None) -> None:
        """Create a mock KMS instance with an optional master secret."""
        self._master_secret = master_secret or hashlib.sha256(os.urandom(32)).digest()
        self._cache: Dict[str, bytes] = {}

    def derive_key(self, identity: str, context: str) -> bytes:
        """Derive a unique key for a given identity and context."""
        cache_key = f"{identity}:{context}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        salt = hashlib.sha256(context.encode("utf-8")).digest()
        key = hashlib.pbkdf2_hmac("sha256", identity.encode("utf-8"), salt, 200_000, dklen=32)
        wrapped = hmac.new(self._master_secret, key, hashlib.sha256).digest()
        self._cache[cache_key] = wrapped
        return wrapped

    def encrypt(self, key: bytes, plaintext: bytes) -> str:
        """Encrypt and authenticate a message using XOR stream + HMAC.

        The method is intentionally simple for auditability. Each ciphertext is
        composed of iv || ciphertext || mac, base64-encoded for transport.
        """
        iv = os.urandom(16)
        keystream = self._expand_keystream(key, iv, len(plaintext))
        ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))
        mac = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(iv + ciphertext + mac).decode("ascii")

    def decrypt(self, key: bytes, token: str) -> bytes:
        """Verify and decrypt a ciphertext produced by :meth:`encrypt`."""
        try:
            data = base64.urlsafe_b64decode(token.encode("ascii"))
        except (base64.binascii.Error, ValueError) as exc:
            raise ValueError("Token was not valid base64") from exc

        iv, rest = data[:16], data[16:]
        ciphertext, mac = rest[:-32], rest[-32:]
        candidate = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(candidate, mac):
            raise ValueError("Ciphertext integrity check failed")
        keystream = self._expand_keystream(key, iv, len(ciphertext))
        return bytes(c ^ k for c, k in zip(ciphertext, keystream))

    @staticmethod
    def _expand_keystream(key: bytes, iv: bytes, length: int) -> bytes:
        material = key + iv
        stream = b""
        counter = 0
        while len(stream) < length:
            stream += hashlib.sha256(material + counter.to_bytes(4, "big")).digest()
            counter += 1
        return stream[:length]


kms_singleton = KMSMock()
