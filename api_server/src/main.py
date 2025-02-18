import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import api_router as router
from core.config import settings
from utils.logger import setup_logger

# 로거 설정
logger = setup_logger()

def create_app() -> FastAPI:
    app = FastAPI(title="Stock LLM API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        reload_includes=['*.py'],
        reload_excludes=['__pycache__', '.pytest_cache', '*.pyc', '*.log'],
        log_level="info"
    )