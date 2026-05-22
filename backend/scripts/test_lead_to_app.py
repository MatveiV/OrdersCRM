import asyncio
import json
import urllib.request


async def main():
    data = json.dumps({"first_name": "Test", "last_name": "Lead2App", "contact_data": "+79991112233", "business_niche": "IT"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/leads/",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req)
        print(f"POST /api/leads/ -> {resp.status}")
        body = json.loads(resp.read())
        print(f"  Created lead #{body['id']}: {body['first_name']}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return

    # Check applications
    from app.core.database import async_session_factory
    from app.models.application import ApplicationModel
    from sqlalchemy import select

    async with async_session_factory() as db:
        result = await db.execute(
            select(ApplicationModel).order_by(ApplicationModel.id.desc()).limit(3)
        )
        apps = result.scalars().all()
        print(f"\nLast 3 applications:")
        for a in apps:
            print(f"  #{a.id}: {a.first_name} {a.last_name} (niche: {a.business_niche})")


asyncio.run(main())
