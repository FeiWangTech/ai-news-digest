import pytest


@pytest.mark.asyncio
async def test_list_user_own_digests(client: AsyncClient, seeded_digests: dict, auth_headers_a: dict):
    resp = await client.get("/digests", headers=auth_headers_a)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_user_b_sees_only_own_digests(
    client: AsyncClient, seeded_digests: dict, auth_headers_b: dict
):
    resp = await client.get("/digests", headers=auth_headers_b)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["id"] in [d.id for d in seeded_digests["user_b"]]


@pytest.mark.asyncio
async def test_get_digest_detail_own(client: AsyncClient, seeded_digests: dict, auth_headers_a: dict):
    digest_id = seeded_digests["user_a"][0].id
    resp = await client.get(f"/digests/{digest_id}", headers=auth_headers_a)
    assert resp.status_code == 200
    assert resp.json()["id"] == digest_id


@pytest.mark.asyncio
async def test_get_digest_detail_other_user_returns_404(
    client: AsyncClient, seeded_digests: dict, auth_headers_b: dict
):
    digest_id = seeded_digests["user_a"][0].id
    resp = await client.get(f"/digests/{digest_id}", headers=auth_headers_b)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_digest_creates_digest(
    client: AsyncClient, auth_headers_a: dict, user_a_pref_or_create
):
    # Ensure no pending digest first (use a fresh user with no digests)
    resp = await client.post("/digests/generate", headers=auth_headers_a)
    assert resp.status_code == 200
    data = resp.json()
    assert "digest_id" in data
    assert data["status"] in ("sent", "failed")

    resp = await client.get("/digests", headers=auth_headers_a)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
