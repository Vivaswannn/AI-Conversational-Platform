import asyncio
import json
import urllib.parse
import urllib.request
import uuid

import websockets


def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=request_headers,
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req).read().decode())


async def main() -> None:
    base = "http://localhost:8000"
    email = f"ws_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!"

    token = post_json(
        f"{base}/auth/register",
        {"email": email, "password": password},
    )["access_token"]

    conversation_id = post_json(
        f"{base}/conversations",
        {"title": "WS Smoke"},
        {"Authorization": f"Bearer {token}"},
    )["id"]

    uri = f"ws://localhost:8000/ws/conversations/{conversation_id}?token={urllib.parse.quote(token)}"
    chunks: list[str] = []
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "Give two short tips for interview anxiety."}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=20)
            data = json.loads(raw)
            if "token" in data:
                chunks.append(data["token"])
            if data.get("done") is True:
                break

    print(
        json.dumps(
            {
                "email": email,
                "conversation_id": conversation_id,
                "received_tokens": len(chunks),
                "assistant_reply": "".join(chunks)[:220],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
