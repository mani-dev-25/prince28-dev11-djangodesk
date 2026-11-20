import pytest
from pydantic import ValidationError

from djangodesk.config import Settings


def test_ready_when_database_available(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["checks"]["database"] is True


def test_ready_when_database_unavailable(client, db_state):
    db_state["up"] = False

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["database"] is False


def test_list_documents_paginates(client):
    response = client.get("/v1/documents", params={"limit": 2})
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_search_filters_records(client):
    response = client.get("/v1/documents", params={"q": "beta"})

    assert [doc["id"] for doc in response.json()["items"]] == ["002"]


def test_search_is_case_insensitive(client):
    response = client.get("/v1/documents", params={"q": "BETA"})

    assert [doc["id"] for doc in response.json()["items"]] == ["002"]


def test_filter_by_metadata(client):
    response = client.get("/v1/documents", params={"category": "guide"})

    assert response.status_code == 200
    assert [doc["id"] for doc in response.json()["items"]] == ["001"]


def test_filter_values_are_returned(client):
    response = client.get("/v1/documents", params={"category": "guide"})

    assert response.json()["filters"] == {"category": "guide"}


def test_invalid_filter_key_returns_400(client):
    response = client.get("/v1/documents", params={"Bad-Name": "test"})

    assert response.status_code == 400


def test_list_without_filters(client):
    response = client.get("/v1/documents")

    assert response.status_code == 200
    assert response.json()["filters"] == {}


def test_get_document_found(client):
    response = client.get("/v1/documents/001")

    assert response.status_code == 200
    assert response.json()["title"] == "Alpha guideline"


def test_missing_document_returns_problem_details(client):
    response = client.get("/v1/documents/999")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["status"] == 404


def test_bad_limit_is_422(client):
    response = client.get("/v1/documents", params={"limit": 0})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "query.limit"


def test_bad_offset_is_422(client):
    response = client.get("/v1/documents", params={"offset": -1})

    assert response.status_code == 422


def test_request_id_is_echoed(client):
    response = client.get(
        "/health",
        headers={"X-Request-ID": "abc123"},
    )

    assert response.headers["X-Request-ID"] == "abc123"


def test_health_is_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_app_refuses_to_start_without_app_env(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
