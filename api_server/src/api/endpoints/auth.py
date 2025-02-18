from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

class UserCreate(BaseModel):
    uid: str
    password: str

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    if len(user.uid) < 4 or len(user.password) < 6:
        raise HTTPException(
            status_code=400, 
            detail="ID는 4자 이상, 비밀번호는 6자 이상이어야 합니다."
        )
    
    if user_service.create_user(user.uid, user.password):
        return {"message": "회원가입이 완료되었습니다."}
    else:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 사용자입니다."
        )

class UserLogin(BaseModel):
    uid: str
    password: str

@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    if user_service.verify_user(user.uid, user.password):
        # 로그인 성공 시 사용자 정보 반환
        return {
            "message": "로그인 성공",
            "user": {
                "uid": user.uid,
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="아이디 또는 비밀번호가 올바르지 않습니다."
        )