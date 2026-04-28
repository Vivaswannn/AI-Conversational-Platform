import os
import pytest
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")

from app.ai.memory import build_chat_history
from langchain_core.messages import HumanMessage, AIMessage


def test_build_chat_history_empty():
    history = build_chat_history([])
    assert history == []


def test_build_chat_history_converts_roles():
    class FakeMsg:
        def __init__(self, role, content):
            self.role = role
            self.content = content

    msgs = [
        FakeMsg("user", "Hello"),
        FakeMsg("assistant", "Hi there!"),
    ]
    history = build_chat_history(msgs)
    assert isinstance(history[0], HumanMessage)
    assert isinstance(history[1], AIMessage)
    assert history[0].content == "Hello"
    assert history[1].content == "Hi there!"


def test_build_chain_input_with_context():
    from app.ai.chain import build_chain_input
    context_chunks = ["chunk one", "chunk two"]
    history = [HumanMessage(content="Hi")]
    user_message = "I feel anxious"

    result = build_chain_input(history, context_chunks, user_message)

    assert "chunk one" in result["context"]
    assert "chunk two" in result["context"]
    assert result["user_message"] == "I feel anxious"
    assert len(result["history"]) == 1


def test_build_chain_input_empty_context():
    from app.ai.chain import build_chain_input
    result = build_chain_input([], [], "hello")
    assert result["context"] == ""
    assert result["user_message"] == "hello"


# --- Integration tests ---

@pytest.mark.asyncio
async def test_create_and_use_conversation(client, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    resp = await client.post("/conversations", json={"title": "My Test Chat"}, headers=headers)
    assert resp.status_code == 201
    convo_id = resp.json()["id"]

    resp = await client.post(
        f"/conversations/{convo_id}/messages",
        json={"content": "I feel stressed about work"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"]["role"] == "user"
    assert data["response"]["role"] == "assistant"


@pytest.mark.asyncio
async def test_crisis_message_returns_safety_response(client, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    resp = await client.post("/conversations", json={}, headers=headers)
    convo_id = resp.json()["id"]

    resp = await client.post(
        f"/conversations/{convo_id}/messages",
        json={"content": "I want to kill myself"},
        headers=headers,
    )
    assert resp.status_code == 200
    response_text = resp.json()["response"]["content"]
    assert "988" in response_text


@pytest.mark.asyncio
async def test_message_history_persisted(client, registered_user):
    headers = {"Authorization": f"Bearer {registered_user['token']}"}

    resp = await client.post("/conversations", json={}, headers=headers)
    convo_id = resp.json()["id"]

    await client.post(f"/conversations/{convo_id}/messages",
                      json={"content": "Hello"}, headers=headers)
    await client.post(f"/conversations/{convo_id}/messages",
                      json={"content": "How are you?"}, headers=headers)

    resp = await client.get(f"/conversations/{convo_id}/messages", headers=headers)
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 4  # 2 user + 2 assistant
