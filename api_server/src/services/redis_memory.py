import redis
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.memory import BaseChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, SystemMessage

class RedisMemory(BaseChatMessageHistory):
    def __init__(self, conversation_id: str, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.conversation_id = conversation_id
        self.input_key: Optional[str] = None
        
    def _get_chat_key(self) -> str:
        return f"chat:{self.conversation_id}"

    def _get_metadata_key(self) -> str:
        return f"chat:{self.conversation_id}:metadata"
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": kwargs
        }
        chat_key = self._get_chat_key()
        self.redis.rpush(chat_key, json.dumps(message))
        
    def add_user_message(self, message: str, **kwargs) -> None:
        self.add_message("user", message, **kwargs)

    def add_ai_message(self, message: str, **kwargs) -> None:
        self.add_message("assistant", message, **kwargs)

    def get_messages(self, last_k: Optional[int] = None) -> List[Dict]:
        chat_key = self._get_chat_key()
        if last_k is None:
            messages = self.redis.lrange(chat_key, 0, -1)
        else:
            messages = self.redis.lrange(chat_key, -last_k, -1)
        return [json.loads(msg) for msg in messages]

    @property
    def messages(self):
        raw_messages = self.get_messages()
        messages = []
        for msg in raw_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
        return messages

    def clear(self) -> None:
        self.redis.delete(self._get_chat_key())
        self.redis.delete(self._get_metadata_key())

    def set_user_id(self, user_id: str) -> None:
        """Set user ID in metadata"""
        self.input_key = user_id
        self.redis.hset(self._get_metadata_key(), "user_id", user_id)

    def get_user_id(self) -> Optional[str]:
        """Get user ID from metadata"""
        return self.redis.hget(self._get_metadata_key(), "user_id")

    def set_metadata(self, key: str, value: Any) -> None:
        """메타데이터 저장"""
        self.redis.hset(self._get_metadata_key(), key, json.dumps(value))

    def get_metadata(self, key: str) -> Optional[Any]:
        """메타데이터 조회"""
        value = self.redis.hget(self._get_metadata_key(), key)
        return json.loads(value) if value else None

    def get_all_metadata(self) -> Dict[str, Any]:
        """전체 메타데이터 조회"""
        metadata = self.redis.hgetall(self._get_metadata_key())
        return {k: json.loads(v) for k, v in metadata.items()}