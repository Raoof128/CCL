"""Demo workloads executed inside the simulated enclave."""

from __future__ import annotations

import hashlib
import json
from typing import Callable, Dict, List

from server.security.logs import get_logger

logger = get_logger(__name__)


def encrypted_keyword_search(documents: List[str], keyword: str) -> Dict[str, int]:
    """Return a count of keyword appearances across documents."""
    normalized = keyword.lower()
    counts = {
        str(doc_id): doc.lower().split().count(normalized) for doc_id, doc in enumerate(documents)
    }
    logger.debug("keyword search complete", extra={"keyword": normalized, "counts": counts})
    return counts


def sealed_secret_manager(
    seal_fn: Callable[[str, Dict[str, str]], str],
    unseal_fn: Callable[[str], Dict[str, str]],
    secret: str,
    identity: str,
) -> Dict[str, str]:
    """Seal and immediately unseal a secret to demonstrate persistence semantics."""
    token = seal_fn(identity, {"secret": secret})
    recovered = unseal_fn(identity)
    return {"token": token, "recovered": recovered["secret"]}


def privacy_preserving_inference(vector: List[float]) -> Dict[str, float]:
    """Compute a simple L2 norm as a stand-in for model inference."""
    norm = sum(v * v for v in vector) ** 0.5
    hashed = hashlib.sha256(json.dumps(vector).encode("utf-8")).hexdigest()
    logger.debug("inference computed", extra={"norm": norm})
    return {"norm": norm, "commitment": hashed}


def integrity_protected_counter(initial: int, increments: int) -> Dict[str, int]:
    """Increment a counter with a simple integrity tag."""
    value = initial
    for _ in range(increments):
        value += 1
    mac = hashlib.sha256(f"{value}:{increments}".encode()).hexdigest()
    return {"counter": value, "mac": mac}
