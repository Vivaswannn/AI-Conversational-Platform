import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services import conversation_service, chat_service
from app.services.auth_service import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


async def _authenticate_ws(token: str) -> str:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token payload")
    return user_id


def _extract_subprotocol_token(header_value: str | None) -> tuple[str | None, str | None]:
    if not header_value:
        return None, None
    for raw in header_value.split(","):
        protocol = raw.strip()
        if protocol.startswith("bearer."):
            return protocol.removeprefix("bearer."), protocol
    return None, None


@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    token: str | None = Query(default=None),
):
    try:
        header_token, selected_subprotocol = _extract_subprotocol_token(
            websocket.headers.get("sec-websocket-protocol")
        )
        ws_token = token or header_token
        if not ws_token:
            raise ValueError("Missing websocket token")
        user_id = await _authenticate_ws(ws_token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # If client requested a bearer subprotocol, echo it back to satisfy browser WS negotiation.
    if selected_subprotocol:
        await websocket.accept(subprotocol=selected_subprotocol)
    else:
        await websocket.accept()
    logger.info("WS connected: user=%s conversation=%s", user_id, conversation_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                content: str = data.get("content", "").strip()
                if not content:
                    await websocket.send_json({"error": "Empty message"})
                    continue
                if len(content) > 4000:
                    await websocket.send_json({"error": "Message too long (max 4000 chars)"})
                    continue
                content = content.replace("\x00", "")
            except (json.JSONDecodeError, AttributeError):
                await websocket.send_json({"error": 'Invalid JSON. Expected {"content": "..."}'})
                continue

            async with AsyncSessionLocal() as db:
                try:
                    await conversation_service.get_conversation(db, conversation_id, user_id)
                except Exception:
                    await websocket.send_json({"error": "Conversation not found"})
                    continue

                async for token_chunk in chat_service.process_message_streaming(
                    db, user_id, conversation_id, content
                ):
                    await websocket.send_json({"token": token_chunk})

            await websocket.send_json({"done": True})

    except WebSocketDisconnect:
        logger.info("WS disconnected: user=%s conversation=%s", user_id, conversation_id)
    except Exception:
        logger.exception("WS error: user=%s conversation=%s", user_id, conversation_id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
