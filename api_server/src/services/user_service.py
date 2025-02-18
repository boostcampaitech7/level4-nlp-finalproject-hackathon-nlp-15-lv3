import redis
import json
import hashlib
from datetime import datetime
from core.config import settings

class UserService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    def _get_user_key(self, uid: str) -> str:
        return f"user:{uid}"
    
    def create_user(self, uid: str, password: str) -> bool:
        """새로운 사용자 생성"""
        user_key = self._get_user_key(uid)
        
        # 이미 존재하는 사용자인지 확인
        if self.redis.exists(user_key):
            return False
            
        # 비밀번호 해싱
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 사용자 정보 저장
        user_data = {
            "uid": uid,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        
        self.redis.hset(user_key, mapping=user_data)
        return True
    
    def verify_user(self, uid: str, password: str) -> bool:
        """사용자 인증"""
        user_key = self._get_user_key(uid)
        user_data = self.redis.hgetall(user_key)
        
        if not user_data:
            return False
            
        # 비밀번호 해싱 후 비교
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        stored_password = user_data.get(b"password", b"").decode()
        
        return stored_password == hashed_password