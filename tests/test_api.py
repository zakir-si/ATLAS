from fastapi.testclient import TestClient

from atlas.api import app

client = TestClient(app)


def test_liveness_and_readiness() -> None:
    assert client.get("/health/live").json()["status"] == "alive"
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_frontend_is_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ATLAS" in response.text


def test_selection_endpoint() -> None:
    response = client.post("/api/v1/select", json={
        "results": [
            {"name": "baseline", "quality": 0.9, "accelerator_hours": 10,
             "peak_memory_gb": 16, "tokens_per_second": 100},
            {"name": "candidate", "quality": 0.88, "accelerator_hours": 6,
             "peak_memory_gb": 10, "tokens_per_second": 120},
        ],
        "min_quality": 0.85,
        "max_accelerator_hours": 8,
    })
    assert response.status_code == 200
    assert response.json()["selected"]["name"] == "candidate"


def test_selection_rejects_no_eligible_run() -> None:
    response = client.post("/api/v1/select", json={
        "results": [{"name": "low", "quality": 0.5, "accelerator_hours": 1,
                     "peak_memory_gb": 1, "tokens_per_second": 1}],
        "min_quality": 0.8, "max_accelerator_hours": 2,
    })
    assert response.status_code == 422


def test_unknown_fields_rejected() -> None:
    response = client.post("/api/v1/select", json={
        "results": [{"name": "run", "quality": 0.8, "accelerator_hours": 1,
                     "peak_memory_gb": 1, "tokens_per_second": 1, "extra": "no"}],
        "min_quality": 0.7, "max_accelerator_hours": 2,
    })
    assert response.status_code == 422
