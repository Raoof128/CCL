"""FastAPI routes for SEV VM simulation."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from server.security.logs import get_logger
from sev.launch_flow import launch_manager

router = APIRouter(prefix="/vm", tags=["sev"])
logger = get_logger(__name__)


class VmLaunchRequest(BaseModel):
    """Request schema for creating a simulated SEV VM."""

    owner: str = Field(..., description="Owner identity", min_length=1, max_length=128)


class VmEncryptRequest(BaseModel):
    """Request schema for encrypting a VM page."""

    vm_id: str = Field(..., description="Target VM identifier", min_length=1)
    page_id: Annotated[int, Field(ge=0, description="Page index")]
    payload: bytes = Field(..., description="Binary data to encrypt", min_length=1, max_length=8192)


class VmLaunchResponse(BaseModel):
    """Response schema for VM launch events."""

    vm_id: str
    vcpu_id: int
    measurement: str


class VmEncryptResponse(BaseModel):
    """Response schema for VM page encryption."""

    vm_id: str
    page_id: int
    measurement: str
    mac: str


class VmAttestationResponse(BaseModel):
    """Response schema for VM attestation reports."""

    vm_id: str
    nonce: str
    measurement: str


@router.post("/launch", response_model=VmLaunchResponse)
def launch_vm(req: VmLaunchRequest) -> VmLaunchResponse:
    """Create a VM, initialise a vCPU, and return measurement."""
    vm = launch_manager.create_vm(owner=req.owner)
    vcpu = vm.launch_vcpu()
    measurement = vm.measure()
    logger.info("VM launched", extra={"vm_id": vm.vm_id, "owner": req.owner})
    return VmLaunchResponse(vm_id=vm.vm_id, vcpu_id=vcpu.id, measurement=measurement)


@router.post("/encrypt", response_model=VmEncryptResponse)
def encrypt(req: VmEncryptRequest) -> VmEncryptResponse:
    """Encrypt a VM memory page and refresh the VM measurement."""
    try:
        result = launch_manager.encrypt_page(req.vm_id, req.page_id, req.payload)
    except KeyError as exc:
        logger.error("Encrypt request for missing VM", extra={"vm_id": req.vm_id})
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return VmEncryptResponse.model_validate(result)


@router.post("/attest", response_model=VmAttestationResponse)
def attest(vm_id: Annotated[str, Query(min_length=1)]) -> VmAttestationResponse:
    """Issue a simulated attestation report for a VM."""
    try:
        return VmAttestationResponse.model_validate(launch_manager.attest(vm_id))
    except KeyError as exc:
        logger.error("Attestation request for missing VM", extra={"vm_id": vm_id})
        raise HTTPException(status_code=404, detail=str(exc)) from exc
