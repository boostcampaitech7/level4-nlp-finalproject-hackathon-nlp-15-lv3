from typing import Generator, Dict
from functools import lru_cache
from fastapi import Depends
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from core.config import settings

@lru_cache()
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        **settings.llm_settings,
        google_api_key=settings.GOOGLE_API_KEY
    )

# 대화별 메모리 저장소
#TODO 이 부분은 추후에 Redis로 대체할 수 있습니다.
#TODO 대화 저장/로드는 별도 모듈로 구현 필요
conv_memories: Dict[str, ConversationBufferWindowMemory] = {}

def get_memory(conv_id: str) -> ConversationBufferWindowMemory:
    """사용자별 Memory 인스턴스 제공"""
    if conv_id not in conv_memories:
        conv_memories[conv_id] = ConversationBufferWindowMemory(input_key="history", k=3)
    return conv_memories[conv_id]