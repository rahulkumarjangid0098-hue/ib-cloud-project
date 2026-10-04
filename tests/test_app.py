import os
import sys

import fakeredis
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import app as app_module  # noqa: E402


@pytest.fixture()
def client():
    app_module.redis_client = fakeredis.FakeRedis(decode_responses=True)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_home_returns_instance_id(client):
    data = client.get("/").get_json()
    assert data["instance"] == app_module.INSTANCE_ID
    assert data["message"] == "Hello from the cluster!"


def test_add_endpoint(client):
    assert client.get("/add/2/3").get_json()["result"] == 5


def test_counter_increments_across_requests(client):
    first = client.get("/").get_json()["total_hits"]
    second = client.get("/").get_json()["total_hits"]
    assert second == first + 1


def test_stats_tracks_per_instance(client):
    client.get("/")
    client.get("/")
    stats = client.get("/stats").get_json()
    assert stats["total_hits"] == 2
    assert stats["per_instance"][app_module.INSTANCE_ID] == 2


def test_unknown_route_404(client):
    assert client.get("/nope").status_code == 404
