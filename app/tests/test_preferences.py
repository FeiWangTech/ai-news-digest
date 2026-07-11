import pytest

def test_preferences_flow(test_client):
    r = test_client.post("/auth/register", json={"email": "p@b.com", "password": "secret123"})
    token = test_client.post("/auth/login", json={"email": "p@b.com", "password": "secret123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    get = test_client.get("/preferences/", headers=headers)
    assert get.status_code == 200
    put = test_client.put("/preferences/", headers=headers, json={"send_time": "09:30", "frequency": "weekly", "sources": ["hackernews"], "topics": ["ML"]})
    assert put.status_code == 200
    assert put.json()["send_time"] == "09:30"
    assert put.json()["frequency"] == "weekly"
    assert put.json()["sources"] == ["hackernews"]
