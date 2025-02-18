from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.memory import BaseMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel
import redis
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class RedisChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, redis_client: redis.Redis, conversation_id: str):
        self.redis = redis_client
        self.conversation_id = conversation_id

    def add_message(self, message: Any) -> None:
        """Redis에 메시지를 저장"""
        role = (
            "assistant" if isinstance(message, AIMessage)
            else "user" if isinstance(message, HumanMessage)
            else "system"
        )
        msg_record = {
            "role": role,
            "content": message.content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        self.redis.rpush(f"chat:{self.conversation_id}", json.dumps(msg_record))

    def clear(self) -> None:
        """대화 이력 삭제"""
        self.redis.delete(f"chat:{self.conversation_id}")

    @property
    def messages(self) -> List[Any]:
        """Redis에서 메시지 목록을 불러와 각 메시지 객체 생성"""
        raw_messages = self.redis.lrange(f"chat:{self.conversation_id}", 0, -1)
        result = []
        for raw in raw_messages:
            data = json.loads(raw.decode()) if isinstance(raw, bytes) else json.loads(raw)
            if data["role"] == "assistant":
                result.append(AIMessage(content=data["content"]))
            elif data["role"] == "user":
                result.append(HumanMessage(content=data["content"]))
            else:
                result.append(SystemMessage(content=data["content"]))
        return result

class RedisMemory(BaseMemory, BaseModel):
    """Redis 기반 메모리 구현"""
    conversation_id: str
    redis_url: str
    _redis_client: Optional[redis.Redis] = None
    def __init__(self, conversation_id: str, redis_url: str):
        super().__init__(conversation_id=conversation_id, redis_url=redis_url)
        print(f"RedisMemory initialized with conversation_id: {conversation_id}")
        self.conversation_id = conversation_id
        self.redis_url = redis_url
        self._redis = redis.from_url(redis_url)

    @property
    def memory_key(self) -> str:
        return "chat_history"

    @property
    def memory_variables(self) -> List[str]:
        """필수 메모리 변수 리스트 반환"""
        return [self.memory_key]

    def _get_chat_key(self) -> str:
        """대화 메시지 저장을 위한 Redis 키 생성"""
        return f"chat:{self.conversation_id}"

    def _get_metadata_key(self) -> str:
        """메타데이터 저장을 위한 Redis 키 생성"""
        return f"chat:{self.conversation_id}:metadata"

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에서 대화 이력 로드"""
        messages = []
        for msg in self.get_messages():
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                messages.append(SystemMessage(content=msg["content"]))
        return {self.memory_key: messages}

    async def aload_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """비동기 메모리 로드"""
        return self.load_memory_variables(inputs)

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """대화 컨텍스트 저장"""
        if "input" in inputs:
            self.add_message("user", inputs["input"])
        if "output" in outputs:
            self.add_message("assistant", outputs["output"])

    async def asave_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """비동기 컨텍스트 저장"""
        self.save_context(inputs, outputs)

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """새로운 메시지 추가
        
        Args:
            role: 메시지 작성자 역할 ("user" 또는 "assistant")
            content: 메시지 내용
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": kwargs
        }
        self._redis.rpush(self._get_chat_key(), json.dumps(message))

    def get_messages(self, last_k: Optional[int] = None) -> List[Dict]:
        """메시지 이력 조회
        
        Args:
            last_k: 마지막 k개의 메시지만 조회할 경우 지정
            
        Returns:
            메시지 목록
        """
        chat_key = self._get_chat_key()
        if last_k is None:
            messages = self._redis.lrange(chat_key, 0, -1)
        else:
            messages = self._redis.lrange(chat_key, -last_k, -1)
        return [json.loads(msg.decode()) if isinstance(msg, bytes) else json.loads(msg) for msg in messages]

    def clear(self) -> None:
        """대화 이력 삭제"""
        self._redis.delete(self._get_chat_key())
        self._redis.delete(self._get_metadata_key())

    # 메타데이터 관련 메서드들은 그대로 유지
    def set_user_id(self, user_id: str) -> None:
        """대화 소유자 ID 설정"""
        self._redis.hset(self._get_metadata_key(), "user_id", user_id)

    def get_user_id(self) -> Optional[str]:
        """대화 소유자 ID 조회"""
        value = self._redis.hget(self._get_metadata_key(), "user_id")
        return value.decode() if value else None

    def set_metadata(self, key: str, value: Any) -> None:
        self._redis.hset(self._get_metadata_key(), key, json.dumps(value))

    def get_metadata(self, key: str) -> Optional[Any]:
        value = self._redis.hget(self._get_metadata_key(), key)
        return json.loads(value) if value else None