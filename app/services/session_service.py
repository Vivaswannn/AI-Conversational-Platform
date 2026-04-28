import json
import logging
from datetime import datetime, timezone

from redis.asyncio import Redis

logger = logging.getLogger(__name__)
SESSION_TTL_SECONDS = 86400  # 24 hours


def _key(user_id: str) -> str:
    return f"session:{user_id}"


async def get_session(redis: Redis, user_id: str) -> dict:
    raw = await redis.get(_key(user_id))
    if raw:
        return json.loads(raw)
    return {}


async def update_session(redis: Redis, user_id: str, **fields) -> None:
    session = await get_session(redis, user_id)
    session.update(fields)
    session["last_active"] = datetime.now(timezone.utc).isoformat()
    await redis.setex(_key(user_id), SESSION_TTL_SECONDS, json.dumps(session))


async def delete_session(redis: Redis, user_id: str) -> None:
    await redis.delete(_key(user_id))
