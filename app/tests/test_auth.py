import pytest

def test_register_login(test_client):
    register = test_client.post("/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert register.status_code == 200
    login = test_client.post("/auth/login", json={"email": "a@b.com", "password": "secret123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = test_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "a@b.com"

def test_duplicate_register(test_client):
    test_client.post("/auth/register", json={"email": "dup@b.com", "password": "secret123"})
    r2 = test_client.post("/auth/register", json={"email": "dup@b.com", "password": "secret123"})
    assert r2.status_code == 400
