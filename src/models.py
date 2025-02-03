from datetime import date
from typing import List, Dict, Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship

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

# Database Models
class Table(SQLModel, table=True):
    """데이터베이스 테이블 모델"""
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: str
    company: str
    securities_firm: str
    report_date: date
    page_number: int
    notes: Optional[str] = None

    # Relationships
    headers: List["TableHeader"] = Relationship(back_populates="table")
    rows: List["TableRow"] = Relationship(back_populates="table")

class TableHeader(SQLModel, table=True):
    """테이블 헤더 모델"""
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    position: int  # Column position (0-based)
    
    # Foreign key
    table_id: int = Field(foreign_key="table.id")
    table: Table = Relationship(back_populates="headers")

class TableRow(SQLModel, table=True):
    """테이블 행 모델"""
    id: Optional[int] = Field(default=None, primary_key=True)
    position: int  # Row position (0-based)
    
    # Foreign key
    table_id: int = Field(foreign_key="table.id")
    table: Table = Relationship(back_populates="rows")

    # Cells in this row
    cells: List["TableCell"] = Relationship(back_populates="row")

class TableCell(SQLModel, table=True):
    """테이블 셀 모델"""
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    position: int  # Column position (0-based)
    
    # Foreign key
    row_id: int = Field(foreign_key="tablerow.id")
    row: TableRow = Relationship(back_populates="cells")
