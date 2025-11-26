"""Integration tests for enclave API routes."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from server.api import app

client = TestClient(app)


def test_keyword_search_workload():
    response = client.post(
        "/enclave/compute",
        json={
            "enclave_name": "demo",
            "workload": "keyword_search",
            "payload": {
                "documents": ["hello secure world", "secure enclaves"],
                "keyword": "secure",
            },
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["result"]["0"] == 1
    assert data["result"]["1"] == 1


def test_invalid_keyword_payload_validation():
    response = client.post(
        "/enclave/compute",
        json={
            "enclave_name": "demo",
            "workload": "keyword_search",
            "payload": {"documents": [123], "keyword": ""},
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_attestation_endpoint():
    response = client.post("/enclave/attest", json={"enclave_name": "demo"})
    assert response.status_code == HTTPStatus.OK
    report = response.json()
    assert "mrenclave" in report
    assert "nonce" in report


def test_sealing_round_trip():
    seal_response = client.post(
        "/enclave/seal",
        json={"enclave_name": "demo", "identity": "alice", "data": {"secret": "value"}},
    )
    assert seal_response.status_code == HTTPStatus.OK
    token = seal_response.json()["token"]

    compute = client.post(
        "/enclave/compute",
        json={
            "enclave_name": "demo",
            "workload": "sealed_secret",
            "payload": {"secret": "value", "identity": "alice"},
        },
    )
    assert compute.status_code == HTTPStatus.OK
    result = compute.json()["result"]
    assert result["recovered"] == "value"
    assert token


def test_counter_validation():
    response = client.post(
        "/enclave/compute",
        json={
            "enclave_name": "demo",
            "workload": "counter",
            "payload": {"initial": 0, "increments": -1},
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
