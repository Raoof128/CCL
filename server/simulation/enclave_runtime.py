"""SGX-style enclave simulation primitives.

The runtime focuses on clarity and safety for educational purposes. It models
measurement, ECALL/OCALL transitions, sealed storage, and attestation without
depending on hardware extensions.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from server.security.kms_mock import kms_singleton
from server.security.logs import get_logger

logger = get_logger(__name__)


@dataclass
class MemoryPage:
    """Represents isolated enclave memory."""

    address: int
    size: int
    data: bytes = field(default_factory=bytes)

    def write(self, content: bytes) -> None:
        """Write data into the page, enforcing bounds."""
        if len(content) > self.size:
            raise ValueError("Page overflow detected")
        self.data = content
        logger.debug("MemoryPage write", extra={"address": self.address, "len": len(content)})

    def read(self) -> bytes:
        """Read data from the page."""
        logger.debug("MemoryPage read", extra={"address": self.address, "len": len(self.data)})
        return self.data


@dataclass
class AttestationReport:
    """Structured attestation report for simulated enclaves."""

    mrenclave: str
    signer: str
    nonce: str
    policy_version: str


class SimulatedEnclave:
    """High-level enclave lifecycle simulator."""

    def __init__(self, name: str, signer: str = "lab") -> None:
        """Instantiate an enclave with default signer and empty pages."""
        self.name = name
        self.signer = signer
        self.pages: List[MemoryPage] = []
        self.loaded = False
        self.mrenclave = ""
        self.sealed_store: Dict[str, str] = {}
        logger.info("SimulatedEnclave created", extra={"enclave": name})

    def load(self, segments: List[bytes]) -> str:
        """Load code/data segments and compute a measurement."""
        if not segments:
            raise ValueError("At least one segment is required to load an enclave")
        for seg in segments:
            if not isinstance(seg, (bytes, bytearray)) or len(seg) == 0:
                raise ValueError("Segments must be non-empty bytes-like objects")

        self.pages = [
            MemoryPage(address=i * 0x1000, size=len(seg), data=bytes(seg))
            for i, seg in enumerate(segments)
        ]
        self.mrenclave = self._measure(self.pages)
        self.loaded = True
        logger.info("Enclave loaded", extra={"enclave": self.name, "mrenclave": self.mrenclave})
        return self.mrenclave

    def _measure(self, pages: List[MemoryPage]) -> str:
        hasher = hashlib.sha256()
        for page in pages:
            hasher.update(page.data)
        hasher.update(self.name.encode("utf-8"))
        hasher.update(self.signer.encode("utf-8"))
        return hasher.hexdigest()

    def enter(self, handler: Callable[["SimulatedEnclave"], Any]) -> Any:
        """Safely enter the enclave and execute a handler."""
        if not self.loaded:
            raise RuntimeError("Enclave not initialized")
        logger.debug("Entering enclave", extra={"enclave": self.name})
        return handler(self)

    def ecall(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a trusted function safely."""
        logger.debug("ECall invoked", extra={"enclave": self.name, "call": name})
        handler = getattr(self, name, None)
        if handler is None or not callable(handler):
            raise AttributeError(f"Unknown ECALL: {name}")
        return handler(*args, **kwargs)

    def ocall(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a transition to the untrusted host."""
        logger.debug("OCALL", extra={"enclave": self.name, "call": name, "payload": payload})
        return {"call": name, "echo": payload}

    def seal(self, identity: str, data: Dict[str, Any]) -> str:
        """Seal JSON-serialisable data to the enclave measurement and identity."""
        if not identity:
            raise ValueError("identity is required")
        key = kms_singleton.derive_key(identity, context=self.mrenclave)
        blob = json.dumps(data, separators=(",", ":")).encode("utf-8")
        token = kms_singleton.encrypt(key, blob)
        self.sealed_store[identity] = token
        logger.info("Data sealed", extra={"enclave": self.name, "identity": identity})
        return token

    def unseal(self, identity: str) -> Dict[str, Any]:
        """Unseal previously sealed data for an identity."""
        token = self.sealed_store.get(identity)
        if token is None:
            raise KeyError("No sealed data for identity")
        key = kms_singleton.derive_key(identity, context=self.mrenclave)
        data = kms_singleton.decrypt(key, token)
        return json.loads(data.decode("utf-8"))

    def attest(self, policy_version: str = "v1") -> AttestationReport:
        """Produce a simulated attestation report with nonce and measurement."""
        nonce = secrets.token_hex(16)
        report = AttestationReport(
            mrenclave=self.mrenclave,
            signer=self.signer,
            nonce=nonce,
            policy_version=policy_version,
        )
        logger.info("Attestation generated", extra={"enclave": self.name, "nonce": nonce})
        return report


class EnclaveRegistry:
    """Manage enclave instances in-memory."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self._instances: Dict[str, SimulatedEnclave] = {}

    def get_or_create(self, name: str) -> SimulatedEnclave:
        """Return an existing enclave or create and load a new one."""
        if name not in self._instances:
            enclave = SimulatedEnclave(name)
            enclave.load([b"init"])
            self._instances[name] = enclave
        return self._instances[name]


enclave_registry = EnclaveRegistry()
