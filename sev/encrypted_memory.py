"""SEV encrypted memory simulator."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict

from server.security.kms_mock import kms_singleton
from server.security.logs import get_logger

logger = get_logger(__name__)


def _derive_page_key(vm_id: str, page_id: int) -> bytes:
    return kms_singleton.derive_key(identity=f"vm:{vm_id}", context=str(page_id))


@dataclass
class EncryptedPage:
    """Encrypted page metadata including ciphertext and MAC."""

    page_id: int
    ciphertext: str
    mac: str


@dataclass
class EncryptedMemory:
    """Manage a set of encrypted pages scoped to a VM."""

    vm_id: str
    pages: Dict[int, EncryptedPage] = field(default_factory=dict)

    def write(self, page_id: int, data: bytes) -> EncryptedPage:
        """Encrypt and store data for a page, returning the stored metadata."""
        key = _derive_page_key(self.vm_id, page_id)
        token = kms_singleton.encrypt(key, data)
        page = EncryptedPage(page_id=page_id, ciphertext=token, mac=self._mac(token))
        self.pages[page_id] = page
        logger.debug("Encrypted page stored", extra={"vm_id": self.vm_id, "page_id": page_id})
        return page

    def read(self, page_id: int) -> bytes:
        """Read and decrypt a stored page, validating integrity."""
        page = self.pages.get(page_id)
        if page is None:
            raise KeyError("Page missing")
        key = _derive_page_key(self.vm_id, page_id)
        data = kms_singleton.decrypt(key, page.ciphertext)
        if not self._verify(page.ciphertext, page.mac):
            raise ValueError("Integrity check failed for page")
        logger.debug("Encrypted page read", extra={"vm_id": self.vm_id, "page_id": page_id})
        return data

    def _mac(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _verify(self, token: str, mac: str) -> bool:
        return self._mac(token) == mac
