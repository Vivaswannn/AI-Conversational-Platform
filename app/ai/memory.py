from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from app.models.message import Message


def build_chat_history(messages: list[Message]) -> list[BaseMessage]:
    """Convert DB Message rows into LangChain message objects for chain history."""
    lc_messages: list[BaseMessage] = []
    for msg in messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
        elif msg.role == "system":
            lc_messages.append(SystemMessage(content=msg.content))
    return lc_messages
