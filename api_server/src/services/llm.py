from functools import lru_cache
from fastapi import Depends
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings
from .redis_memory import RedisMemory

@lru_cache()
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        **settings.llm_settings,
        google_api_key=settings.GOOGLE_API_KEY
    )

def get_memory(conv_id: str) -> RedisMemory:
    """Redis 기반 Memory 인스턴스 제공"""
    return RedisMemory(
        conversation_id=conv_id,
        redis_url=settings.REDIS_URL
    )