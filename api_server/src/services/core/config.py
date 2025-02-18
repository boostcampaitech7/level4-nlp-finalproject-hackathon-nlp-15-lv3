from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Dict, Any
import os


load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_CX: str = os.getenv("GOOGLE_CX", "")
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 30002
    
    collection_name: str = "pdf_text_collection"
    
    llm_settings: Dict[str, Any] = {
        "model": "gemini-1.5-flash",
        "temperature": 0,
        "max_output_tokens": 1024,
    }

    model_config: Dict[str, Any] = {
        "env_file": ".env",
        "case_sensitive": False
    }
    
    vector_db: Dict[str, Any] = {
        "model": "intfloat/multilingual-e5-small", #"kakaobank/kf-deberta-base",
        "chroma_db_dir": os.getenv("CHROMA_DB_DIR", "/data/ephemeral/chroma_db"),
        "max_chunk_size": 1024,
        "num_chunk_overlap": 256,
    }

settings = Settings()