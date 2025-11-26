"""Integration tests for SEV VM API routes."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from server.api import app

client = TestClient(app)


def test_vm_launch_and_encrypt():
    launch = client.post("/vm/launch", json={"owner": "researcher"})
    assert launch.status_code == HTTPStatus.OK
    vm_info = launch.json()
    vm_id = vm_info["vm_id"]

    encrypt = client.post(
        "/vm/encrypt",
        json={"vm_id": vm_id, "page_id": 1, "payload": "ZGVtbw=="},
    )
    assert encrypt.status_code == HTTPStatus.OK
    payload = encrypt.json()
    assert payload["vm_id"] == vm_id
    assert "measurement" in payload

    attest = client.post("/vm/attest", params={"vm_id": vm_id})
    assert attest.status_code == HTTPStatus.OK
    report = attest.json()
    assert report["vm_id"] == vm_id
    assert "measurement" in report


def test_encrypt_missing_vm_returns_not_found():
    response = client.post(
        "/vm/encrypt",
        json={"vm_id": "unknown", "page_id": 0, "payload": "ZGVtbw=="},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
