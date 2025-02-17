from fastapi import APIRouter
from api.endpoints import api, chat, indexing, rag, retrieval, web_rag, recommend_questions

# API 라우터 생성
api_router = APIRouter()

# 각 엔드포인트 라우터 등록
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    indexing.router,
    prefix="/indexing",
    tags=["indexing"]
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["rag"]
)

api_router.include_router(
    retrieval.router,
    prefix="/retrieval",
    tags=["retrieval"]
)

api_router.include_router(
    web_rag.router,
    prefix="/web_rag",
    tags=["web_rag"]
)

api_router.include_router(
    recommend_questions.router,
    prefix="/recommend",
    tags=["recommend"]
)

api_router.include_router(
    api.router,
    prefix="/api",
    tags=["api"]
)

# 라우터 export
__all__ = ["api_router"]