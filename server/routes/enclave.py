"""FastAPI routes for SGX-style enclave simulation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server.security.logs import get_logger
from server.simulation.enclave_runtime import enclave_registry
from server.workloads import workloads

logger = get_logger(__name__)

router = APIRouter(prefix="/enclave", tags=["enclave"])


class ComputeRequest(BaseModel):
    """Request schema for invoking a demo workload inside an enclave."""

    enclave_name: str = Field(..., description="Identifier for the enclave instance", min_length=1)
    workload: Literal["keyword_search", "sealed_secret", "inference", "counter"] = Field(
        ..., description="Name of the supported demo workload"
    )
    payload: Dict[str, object] = Field(
        default_factory=dict, description="Workload-specific parameters"
    )


class ComputeResponse(BaseModel):
    """Response containing enclave measurement and workload result."""

    mrenclave: str
    result: Dict[str, object]


class AttestationResponse(BaseModel):
    """Response schema for attestation reports."""

    mrenclave: str
    signer: str
    nonce: str
    policy_version: str


class SealResponse(BaseModel):
    """Response schema for sealed payloads."""

    token: str


class AttestationRequest(BaseModel):
    """Request schema for attestation operations."""

    enclave_name: str = Field(..., min_length=1)
    policy_version: str = Field("v1", description="Requested policy version", min_length=1)


class SealRequest(BaseModel):
    """Request schema for sealing data to an enclave-bound identity."""

    enclave_name: str = Field(..., min_length=1)
    identity: str = Field(..., min_length=1)
    data: Dict[str, object] = Field(default_factory=dict)


def _validate_keyword_payload(payload: Dict[str, object]) -> Dict[str, object]:
    documents = payload.get("documents", [])
    keyword = payload.get("keyword", "")
    if not isinstance(documents, list) or not all(isinstance(d, str) for d in documents):
        raise HTTPException(status_code=422, detail="documents must be a list of strings")
    if not isinstance(keyword, str) or not keyword:
        raise HTTPException(status_code=422, detail="keyword must be a non-empty string")
    return {"documents": documents, "keyword": keyword}


def _validate_sealed_payload(payload: Dict[str, object]) -> Dict[str, object]:
    secret = payload.get("secret")
    identity = payload.get("identity")
    if not isinstance(secret, str) or not isinstance(identity, str):
        raise HTTPException(status_code=422, detail="secret and identity must be strings")
    if not secret or not identity:
        raise HTTPException(status_code=422, detail="secret and identity cannot be empty")
    return {"secret": secret, "identity": identity}


def _validate_inference_payload(payload: Dict[str, object]) -> Dict[str, object]:
    vector = payload.get("vector", [])
    if not isinstance(vector, list) or not all(isinstance(v, (int, float)) for v in vector):
        raise HTTPException(status_code=422, detail="vector must be a list of numbers")
    return {"vector": [float(v) for v in vector]}


def _validate_counter_payload(payload: Dict[str, object]) -> Dict[str, object]:
    initial = payload.get("initial", 0)
    increments = payload.get("increments", 1)
    if not isinstance(initial, int) or not isinstance(increments, int):
        raise HTTPException(status_code=422, detail="initial and increments must be integers")
    if increments < 0:
        raise HTTPException(status_code=422, detail="increments must be non-negative")
    return {"initial": initial, "increments": increments}


@router.post("/compute", response_model=ComputeResponse)
def compute(req: ComputeRequest) -> ComputeResponse:
    """Run a supported workload inside a simulated enclave."""
    enclave = enclave_registry.get_or_create(req.enclave_name)
    if not enclave.loaded:
        logger.error("Enclave requested before initialization", extra={"enclave": req.enclave_name})
        raise HTTPException(status_code=400, detail="Enclave not initialized")

    if req.workload == "keyword_search":
        params = _validate_keyword_payload(req.payload)
        result = workloads.encrypted_keyword_search(**params)
    elif req.workload == "sealed_secret":
        params = _validate_sealed_payload(req.payload)
        result = workloads.sealed_secret_manager(
            enclave.seal, enclave.unseal, params["secret"], params["identity"]
        )
    elif req.workload == "inference":
        params = _validate_inference_payload(req.payload)
        result = workloads.privacy_preserving_inference(**params)
    else:  # "counter"
        params = _validate_counter_payload(req.payload)
        result = workloads.integrity_protected_counter(**params)

    logger.info("Workload executed", extra={"enclave": req.enclave_name, "workload": req.workload})
    return ComputeResponse(mrenclave=enclave.mrenclave, result=result)


@router.post("/attest", response_model=AttestationResponse)
def attest(req: AttestationRequest) -> AttestationResponse:
    """Generate an attestation report for a given enclave instance."""
    enclave = enclave_registry.get_or_create(req.enclave_name)
    report = enclave.attest(policy_version=req.policy_version)
    return AttestationResponse.model_validate(asdict(report))


@router.post("/seal", response_model=SealResponse)
def seal(req: SealRequest) -> SealResponse:
    """Seal arbitrary JSON-serialisable data to an identity within an enclave."""
    enclave = enclave_registry.get_or_create(req.enclave_name)
    try:
        token = enclave.seal(req.identity, req.data)
    except ValueError as exc:  # pragma: no cover - defensive path
        logger.exception("Sealing failed", extra={"enclave": req.enclave_name})
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SealResponse(token=token)
