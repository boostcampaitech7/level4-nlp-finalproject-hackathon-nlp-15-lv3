from typing import Generator
from functools import lru_cache
from fastapi import Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables.base import Runnable
from langchain_core.memory import BaseMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory
from core.config import settings

@lru_cache()
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        **settings.llm_settings,
        google_api_key=settings.GOOGLE_API_KEY
    )

@lru_cache()
def get_memory() -> ConversationBufferWindowMemory:
    """Memory 인스턴스를 싱글톤으로 제공"""
    return ConversationBufferWindowMemory(input_key="history", k=3)
