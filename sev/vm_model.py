"""Lightweight AMD SEV-style VM model."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Dict, List

from server.security.logs import get_logger
from sev.encrypted_memory import EncryptedMemory

logger = get_logger(__name__)


@dataclass
class VcpuState:
    """Minimal vCPU representation for simulation."""

    id: int
    registers: Dict[str, int] = field(default_factory=dict)


@dataclass
class SimulatedVM:
    """Simulated VM with encrypted memory and attestation helpers."""

    vm_id: str
    owner: str
    memory: EncryptedMemory
    vcpus: List[VcpuState] = field(default_factory=list)
    measurement: str | None = None

    def launch_vcpu(self) -> VcpuState:
        """Instantiate a new vCPU and append it to the VM."""
        vcpu = VcpuState(id=len(self.vcpus), registers={"rip": 0, "rsp": 0})
        self.vcpus.append(vcpu)
        logger.info("vCPU launched", extra={"vm_id": self.vm_id, "vcpu": vcpu.id})
        return vcpu

    def measure(self) -> str:
        """Generate a measurement over VM metadata and encrypted pages."""
        hasher = hashlib.sha256()
        hasher.update(self.vm_id.encode())
        hasher.update(self.owner.encode())
        for page_id, page in sorted(self.memory.pages.items()):
            hasher.update(page.ciphertext.encode("utf-8"))
            hasher.update(page.mac.encode("utf-8"))
            hasher.update(str(page_id).encode())
        self.measurement = hasher.hexdigest()
        logger.info("VM measured", extra={"vm_id": self.vm_id, "measurement": self.measurement})
        return self.measurement

    def attest(self) -> Dict[str, str]:
        """Return a simulated attestation report with nonce and measurement."""
        nonce = secrets.token_hex(16)
        if self.measurement is None:
            self.measure()
        report = {"vm_id": self.vm_id, "nonce": nonce, "measurement": self.measurement}
        logger.info("VM attestation issued", extra={"vm_id": self.vm_id, "nonce": nonce})
        return report
