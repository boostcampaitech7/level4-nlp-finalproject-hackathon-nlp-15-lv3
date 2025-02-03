from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date

class TableMetadata(BaseModel):
    file_name: str
    company: str
    securities_firm: str
    report_date: date
    page_number: int

class TableData(BaseModel):
    metadata: TableMetadata
    headers: List[str]
    rows: List[Dict[str, str]]
    table_type: Optional[str] = None  # e.g., "financial", "metrics", etc.
    notes: Optional[str] = None
