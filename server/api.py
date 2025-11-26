"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from server.routes import enclave, sev
from server.security.logs import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
app = FastAPI(title="Confidential Computing Lab", version="0.1.0")


@app.get("/health")
def health() -> dict:
    """Return a lightweight heartbeat."""
    logger.debug("Health check invoked")
    return {"status": "ok"}


app.include_router(enclave.router)
app.include_router(sev.router)
