# tests/integration/test_main_endpoints.py

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_index_page(client: TestClient):
    """GET / should render the index template."""
    resp = client.get("/")
    assert resp.status_code == 200
    # Basic smoke check: page contains the headline
    assert "Hello World" in resp.text


@pytest.mark.parametrize("payload, field", [({"a": "x", "b": 2}, "a"), ({"a": 1}, "b")])
def test_validation_errors_add_endpoint(client: TestClient, payload, field):
    """POST /add should return a 400 with a helpful error message for invalid input."""
    resp = client.post("/add", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert "error" in body
    # Accept either Pydantic's type message or our validator's message text
    assert (field in body["error"]) or ("Input should be a valid number" in body["error"]) or (
        "Both a and b must be numbers" in body["error"]
    )


def test_divide_internal_server_error_path(client: TestClient, monkeypatch):
    """Force an unexpected exception in divide to exercise the 500 handler."""
    import main as main_module

    def boom(a, b):
        raise RuntimeError("boom")

    # Patch divide symbol referenced by the route handler in main.py
    monkeypatch.setattr(main_module, "divide", boom)

    resp = client.post("/divide", json={"a": 10, "b": 2})
    assert resp.status_code == 500
    assert resp.json().get("error") == "Internal Server Error"
