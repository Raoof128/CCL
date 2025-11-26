# API Reference

All endpoints are served by the FastAPI application defined in `server/api.py`. Requests and responses use JSON unless otherwise noted. Pydantic validation enforces parameter constraints; invalid inputs return HTTP 422.

## Health
- `GET /health` → `{ "status": "ok" }`

## Enclave Endpoints
- `POST /enclave/compute`
  - Body: `{ "enclave_name": "demo", "workload": "keyword_search|sealed_secret|inference|counter", "payload": {...} }`
  - Workload payloads:
    - `keyword_search`: `{"documents": ["..."], "keyword": "term"}`
    - `sealed_secret`: `{"secret": "value", "identity": "user"}`
    - `inference`: `{"vector": [1.0, 2.0]}`
    - `counter`: `{"initial": 0, "increments": 3}`
  - Response: `{ "mrenclave": "<sha256>", "result": {...} }`

- `POST /enclave/attest`
  - Body: `{ "enclave_name": "demo", "policy_version": "v1" }`
  - Response model: `{ "mrenclave": "...", "signer": "lab", "nonce": "...", "policy_version": "v1" }`

- `POST /enclave/seal`
  - Body: `{ "enclave_name": "demo", "identity": "user", "data": {"secret": "value"} }`
  - Response model: `{ "token": "<base64>" }`

## SEV VM Endpoints
- `POST /vm/launch`
  - Body: `{ "owner": "alice" }`
  - Response model: `{ "vm_id": "...", "vcpu_id": 0, "measurement": "<sha256>" }`

- `POST /vm/encrypt`
  - Body: `{ "vm_id": "...", "page_id": 0, "payload": "<base64>" }`
  - Response model: `{ "vm_id": "...", "page_id": 0, "measurement": "<sha256>", "mac": "..." }`
  - Notes: `payload` is base64-decoded into bytes by FastAPI before processing. Maximum size is 8192 bytes.

- `POST /vm/attest`
  - Query: `vm_id=<id>`
  - Response model: `{ "vm_id": "...", "nonce": "...", "measurement": "<sha256>" }`

## Error Handling
- 4xx errors return a JSON payload with `{"detail": "reason"}`.
- Input validation failures emit HTTP 422 with structured error details from FastAPI.
