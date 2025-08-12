import pytest
import httpx
from asgi_lifespan import LifespanManager
from app.main import app


@pytest.mark.asyncio
async def test_create_list_get_update_delete():
    async with LifespanManager(app):  # <-- important
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            # create
            r = await ac.post("/items/", json={"name": "t1", "description": "d1"})
            assert r.status_code == 201
            item = r.json()
            iid = item["id"]

            # list
            r = await ac.get("/items/?limit=10")
            assert r.status_code == 200
            assert any(x["id"] == iid for x in r.json())

            # get
            r = await ac.get(f"/items/{iid}")
            assert r.status_code == 200
            assert r.json()["name"] == "t1"

            # update
            r = await ac.patch(f"/items/{iid}", json={"description": "d1-up"})
            assert r.status_code == 200
            assert r.json()["description"] == "d1-up"

            # delete
            r = await ac.delete(f"/items/{iid}")
            assert r.status_code == 204

            # gone
            r = await ac.get(f"/items/{iid}")
            assert r.status_code == 404