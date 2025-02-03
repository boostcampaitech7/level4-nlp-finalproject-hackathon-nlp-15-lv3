from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date

class TableMetadata(BaseModel):
    """테이블 메타데이터 모델"""
    file_name: str
    company: str
    securities_firm: str
    report_date: date
    page_number: int

class TableData(BaseModel):
    """테이블 데이터 모델"""
    metadata: TableMetadata
    headers: List[str]
    rows: List[List[str]]  # Raw rows as lists of strings
    notes: Optional[str] = None
