from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.groq_service import chat_wariga
from app.services.chat_context_service import (
    build_chat_database_context,
    is_calendar_question,
)

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)


@router.post("")
def chat(payload: ChatRequest):
    try:
        messages = [message.model_dump() for message in payload.messages]

        if not is_calendar_question(messages):
            return {
                "success": True,
                "data": {
                    "answer": (
                        "Maaf, saya hanya dapat menjawab pertanyaan yang "
                        "berkaitan dengan kalender Bali dan Wariga."
                    ),
                    "model": "rule",
                },
            }

        database_context = build_chat_database_context(messages)
        answer = chat_wariga(messages, database_context)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return {
        "success": True,
        "data": {
            "answer": answer,
            "model": "groq",
        },
    }
