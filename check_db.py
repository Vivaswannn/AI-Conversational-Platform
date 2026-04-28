"""Quick database diagnostic script."""
import asyncio
import asyncpg
from app.config import get_settings


async def main():
    settings = get_settings()
    # asyncpg uses a plain postgres:// URL
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Connecting to: {url}")
    try:
        conn = await asyncpg.connect(url)
    except Exception as e:
        print(f"[FAIL] Cannot connect: {e}")
        return

    print("[OK] Connected")

    tables = await conn.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    )
    names = [r["tablename"] for r in tables]
    print(f"[OK] Tables found: {names}")

    expected = {"users", "conversations", "messages", "crisis_events", "alembic_version"}
    missing = expected - set(names)
    if missing:
        print(f"[WARN] Missing tables: {missing}")
    else:
        print("[OK] All expected tables present")

    # Test round-trip insert / delete
    try:
        await conn.execute(
            "INSERT INTO users(id, email, hashed_password) VALUES($1,$2,$3)",
            "00000000-0000-0000-0000-000000000000",
            "db_test@example.com",
            "hashed",
        )
        await conn.execute(
            "DELETE FROM users WHERE id=$1",
            "00000000-0000-0000-0000-000000000000",
        )
        print("[OK] Read/write round-trip succeeded")
    except Exception as e:
        print(f"[FAIL] Read/write test: {e}")

    await conn.close()


asyncio.run(main())
