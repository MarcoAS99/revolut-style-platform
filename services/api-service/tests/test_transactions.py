import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_idempotent_create_transaction():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "account_id": "11111111-1111-1111-1111-111111111111",
            "amount": "10.00",
            "currency": "EUR",
            "country": "PT",
        }

        r1 = await client.post("/api/transactions", json=payload, headers={"Idempotency-Key": "k1"})
        assert r1.status_code in (200, 201)
        tx1 = r1.json()

        r2 = await client.post("/api/transactions", json=payload, headers={"Idempotency-Key": "k1"})
        assert r2.status_code in (200, 201)
        tx2 = r2.json()

        assert tx1["id"] == tx2["id"]
