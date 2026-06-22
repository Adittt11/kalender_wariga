from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import GROQ_MODEL, OPENAI_LATEST_MODEL, OPENAI_MINI_MODEL
from app.services.chat_context_service import (
    build_dewasa_direct_answer,
    build_chat_database_context,
    extract_latest_date,
    get_latest_user_message,
    is_calendar_question,
    is_dewasa_search_question,
    is_monthly_calendar_question,
)
from app.services.groq_service import chat_wariga as chat_wariga_groq
from app.services.openai_service import chat_wariga as chat_wariga_openai
from app.services.openai_service import interpret_calendar_date

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)
    model: Literal["groq", "gpt54_mini", "gpt_latest"] = "gpt54_mini"


CHAT_MODEL_OPTIONS = {
    "groq": {
        "provider": "groq",
        "model": GROQ_MODEL,
        "label": "Groq",
    },
    "gpt54_mini": {
        "provider": "openai",
        "model": OPENAI_MINI_MODEL,
        "label": "GPT 5.4 Mini",
    },
    "gpt_latest": {
        "provider": "openai",
        "model": OPENAI_LATEST_MODEL,
        "label": "GPT 5.5",
    },
}


def clean_chat_answer(answer):
    return str(answer or "").replace("**", "").replace("*", "").strip()


@router.post("")
def chat(payload: ChatRequest):
    try:
        messages = [message.model_dump() for message in payload.messages]
        latest_user_message = get_latest_user_message(messages)
        dewasa_answer = build_dewasa_direct_answer(latest_user_message)

        if dewasa_answer:
            return {
                "success": True,
                "data": {
                    "answer": clean_chat_answer(dewasa_answer),
                    "model": "database",
                    "model_key": "dewasa_direct",
                    "model_name": "dewasa_database",
                    "model_label": "Database Dewasa Ayu",
                },
            }

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

        ai_resolved_date = None

        if (
            not extract_latest_date(messages)
            and not is_dewasa_search_question(latest_user_message)
            and not is_monthly_calendar_question(latest_user_message)
        ):
            ai_resolved_date = interpret_calendar_date(latest_user_message)

        database_context = build_chat_database_context(
            messages,
            ai_resolved_date=ai_resolved_date,
        )
        selected_model = CHAT_MODEL_OPTIONS[payload.model]

        if selected_model["provider"] == "groq":
            answer = chat_wariga_groq(
                messages,
                database_context,
                model=selected_model["model"],
            )
        else:
            answer = chat_wariga_openai(
                messages,
                database_context,
                model=selected_model["model"],
            )
    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return {
        "success": True,
        "data": {
            "answer": clean_chat_answer(answer),
            "model": selected_model["provider"],
            "model_key": payload.model,
            "model_name": selected_model["model"],
            "model_label": selected_model["label"],
        },
    }
