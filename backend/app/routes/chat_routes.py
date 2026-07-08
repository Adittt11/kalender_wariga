from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import GROQ_MODEL, OPENAI_LATEST_MODEL, OPENAI_MINI_MODEL
from app.services.chat_context_service import (
    build_chat_database_context,
    extract_latest_date,
    get_latest_user_message,
    is_calendar_question,
    is_dewasa_search_question,
    is_monthly_calendar_question,
)
from app.services.groq_service import chat_wariga as chat_wariga_groq
from app.services.intent_service import classify_chat_intent
from app.services.openai_service import chat_wariga as chat_wariga_openai
from app.services.openai_service import interpret_calendar_date

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=50000)


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


def normalize_followup_text(value):
    return " ".join(str(value or "").lower().split())


def is_followup_detail_request(value):
    normalized = normalize_followup_text(value)

    if not normalized:
        return False

    followup_keywords = (
        "jawab lengkap",
        "jawab secara lengkap",
        "jawab detail",
        "jawab secara detail",
        "jawab rinci",
        "jawab secara rinci",
        "jelaskan lengkap",
        "jelaskan secara lengkap",
        "jelaskan detail",
        "jelaskan secara detail",
        "jelaskan rinci",
        "jelaskan secara rinci",
        "lebih lengkap",
        "lebih detail",
        "lebih rinci",
        "detailkan",
        "rincikan",
        "simpulkan",
        "buat kesimpulan",
        "kasih kesimpulan",
        "ringkas",
        "ringkaskan",
        "lebih singkat",
        "lebih pendek",
        "pendekkan",
        "persingkat",
        "buat paragraf",
        "buat dalam paragraf",
        "buat dalam bentuk paragraf",
        "jadikan paragraf",
        "ubah jadi paragraf",
        "dalam bentuk paragraf",
        "jabarkan",
        "jabar",
        "jabarkan lagi",
        "jabarkan lebih",
        "kembangkan",
        "kembangkan masing",
        "jelaskan masing",
        "uraikan masing",
        "sesuaikan",
        "jelaskan lagi",
        "jelaskan lebih",
        "ceritakan lebih",
        "ceritakan lagi",
        "lanjutkan",
        "lanjut",
        "uraikan",
        "perjelas",
        "buat lebih panjang",
        "tambahin",
        "tambahkan detail",
        "detail lagi",
        "rinci lagi",
        "lengkapi",
    )

    if any(keyword in normalized for keyword in followup_keywords):
        return True

    action_words = (
        "jawab",
        "jelaskan",
        "terangkan",
        "uraikan",
        "buat",
        "bikin",
        "ubah",
        "jadikan",
        "susun",
        "tulis",
    )
    detail_words = (
        "lengkap",
        "detail",
        "rinci",
        "panjang",
        "pendek",
        "singkat",
        "ringkas",
        "kesimpulan",
        "paragraf",
        "jabarkan",
        "jabar",
        "kembangkan",
    )

    return (
        any(word in normalized for word in action_words)
        and any(word in normalized for word in detail_words)
        and len(normalized.split()) <= 12
    )


def get_previous_user_messages(messages):
    """Return all previous user messages (excluding the latest one), newest first."""
    seen_latest = False
    result = []

    for message in reversed(messages):
        if message["role"] != "user":
            continue

        if not seen_latest:
            seen_latest = True
            continue

        result.append(message["content"])

    return result


@router.post("")
def chat(payload: ChatRequest):
    try:
        messages = [message.model_dump() for message in payload.messages]
        latest_user_message = get_latest_user_message(messages)
        intent_info = classify_chat_intent(latest_user_message)

        if intent_info.get("intent") == "tidak_relevan" and is_followup_detail_request(latest_user_message):
            # Scan back through all previous user messages to find one with a valid intent
            for prev_message in get_previous_user_messages(messages):
                if not prev_message:
                    continue

                previous_intent = classify_chat_intent(prev_message)

                # Skip if this previous message is also a follow-up (e.g. "simpulkan")
                if previous_intent.get("intent") == "tidak_relevan" and is_followup_detail_request(prev_message):
                    continue

                if previous_intent.get("intent") != "tidak_relevan":
                    intent_info = {
                        **previous_intent,
                        "followup_request": latest_user_message,
                        "followup_from": prev_message,
                    }
                    break

        if intent_info.get("intent") == "tidak_relevan" and not is_calendar_question(messages):
            return {
                "success": True,
                "data": {
                    "answer": (
                        "Matur suksma. Sebagai asisten Tanya Wariga AI, saya hanya dapat membantu "
                        "menjawab pertanyaan seputar Kalender Bali dan Wariga. Ada yang bisa saya bantu "
                        "seputar topik ini?"
                    ),
                    "model": "rule",
                    "intent": intent_info,
                },
            }

        ai_resolved_date = None

        if (
            not intent_info.get("date")
            and not extract_latest_date(messages)
            and intent_info.get("intent") not in ("dewasa_ayu", "hari_raya_bulanan")
            and not is_dewasa_search_question(latest_user_message)
            and not is_monthly_calendar_question(latest_user_message)
        ):
            ai_resolved_date = interpret_calendar_date(latest_user_message)

        database_context = build_chat_database_context(
            messages,
            ai_resolved_date=ai_resolved_date,
            intent_info=intent_info,
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
            "intent": intent_info,
        },
    }
