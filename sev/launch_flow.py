"""Simulated SEV launch flow."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict

from server.security.logs import get_logger
from sev.encrypted_memory import EncryptedMemory
from sev.vm_model import SimulatedVM

logger = get_logger(__name__)


@dataclass
class SevLaunchManager:
    """Manage lifecycle of simulated SEV VMs."""

    vms: Dict[str, SimulatedVM] = field(default_factory=dict)

    def create_vm(self, owner: str) -> SimulatedVM:
        """Create a new VM with empty encrypted memory."""
        vm_id = os.urandom(6).hex()
        vm = SimulatedVM(vm_id=vm_id, owner=owner, memory=EncryptedMemory(vm_id=vm_id))
        self.vms[vm_id] = vm
        logger.info("VM created", extra={"vm_id": vm_id, "owner": owner})
        return vm

    def encrypt_page(self, vm_id: str, page_id: int, data: bytes) -> Dict[str, str]:
        """Encrypt a page for a given VM and update measurement."""
        vm = self._require_vm(vm_id)
        page = vm.memory.write(page_id, data)
        measurement = vm.measure()
        return {"vm_id": vm_id, "page_id": page_id, "measurement": measurement, "mac": page.mac}

    def launch_vcpu(self, vm_id: str) -> Dict[str, int | str]:
        """Launch a vCPU on an existing VM."""
        vm = self._require_vm(vm_id)
        vcpu = vm.launch_vcpu()
        return {"vm_id": vm_id, "vcpu_id": vcpu.id}

    def attest(self, vm_id: str) -> Dict[str, str]:
        """Produce a simulated attestation report."""
        vm = self._require_vm(vm_id)
        return vm.attest()

    def _require_vm(self, vm_id: str) -> SimulatedVM:
        vm = self.vms.get(vm_id)
        if vm is None:
            raise KeyError("VM not found")
        return vm


launch_manager = SevLaunchManager()
