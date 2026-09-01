from tests.conftest import AUTH


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["db"] is True
    assert body["status"] == "ok"
    assert "x-request-id" in r.headers


def test_health_is_public(client):
    r = client.get("/health")
    assert r.status_code == 200
    # no API key required
    r2 = client.get("/health", headers=AUTH)
    assert r2.status_code == 200
