import pytest


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "securepwd123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, seeded_users: dict):
    resp = await client.post("/auth/register", json={
        "email": "a@example.com",
        "password": "securepwd123",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seeded_users: dict):
    resp = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "password1",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_bad_password(client: AsyncClient, seeded_users: dict):
    resp = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_read_me_authenticated(client: AsyncClient, auth_headers_a: dict):
    resp = await client.get("/auth/me", headers=auth_headers_a)
    assert resp.status_code == 200
    assert resp.json()["email"] == "a@example.com"


@pytest.mark.asyncio
async def test_read_me_unauthorized(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, auth_headers_a: dict):
    # login to get refresh token
    login = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "password1",
    })
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert resp.json()["access_token"] is not None


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, seeded_users: dict, db):
    resp = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "password1",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/auth/change-password", headers=headers, json={
        "current_password": "password1",
        "new_password": "newpassword123",
    })
    assert resp.status_code == 200

    # old password should fail
    resp = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "password1",
    })
    assert resp.status_code == 401

    # new password should work
    resp = await client.post("/auth/login", json={
        "email": "a@example.com",
        "password": "newpassword123",
    })
    assert resp.status_code == 200
