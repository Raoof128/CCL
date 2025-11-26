"""Unit tests for the mock KMS to ensure integrity protections."""

import pytest

from server.security.kms_mock import KMSMock


def test_encrypt_decrypt_round_trip():
    kms = KMSMock(master_secret=b"static-secret-for-tests")
    key = kms.derive_key("alice", "context")
    token = kms.encrypt(key, b"payload")
    recovered = kms.decrypt(key, token)
    assert recovered == b"payload"


def test_tampering_detection():
    kms = KMSMock(master_secret=b"static-secret-for-tests")
    key = kms.derive_key("bob", "context")
    token = kms.encrypt(key, b"payload")
    tampered = token[::-1]

    with pytest.raises(ValueError) as excinfo:
        kms.decrypt(key, tampered)

    assert "integrity" in str(excinfo.value) or "valid base64" in str(excinfo.value)
