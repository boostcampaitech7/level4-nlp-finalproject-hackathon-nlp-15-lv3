"""테이블 저장 테스트"""

import pytest
from datetime import date
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.models import TableData, TableMetadata, Table, TableHeader, TableRow, TableCell
from src.storage.storer import TableStorer

@pytest.fixture
def session():
    """Create in-memory database session for testing"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def sample_table_data():
    """Create sample table data for testing"""
    return TableData(
        metadata=TableMetadata(
            file_name="test.pdf",
            company="삼성전자",
            securities_firm="신한투자증권",
            report_date=date(2024, 1, 1),
            page_number=1
        ),
        headers=["항목", "2023", "2024E"],
        rows=[
            ["매출액", "100", "120"],
            ["영업이익", "10", "15"]
        ],
        notes="예상 실적"
    )

def test_store_table(session, sample_table_data):
    """테이블 저장 테스트"""
    storer = TableStorer(session)
    table = storer.store_table(sample_table_data)

    # Check table metadata
    assert table.file_name == "test.pdf"
    assert table.company == "삼성전자"
    assert table.securities_firm == "신한투자증권"
    assert table.report_date == date(2024, 1, 1)
    assert table.page_number == 1
    assert table.notes == "예상 실적"

    # Check headers
    assert len(table.headers) == 3
    headers = sorted(table.headers, key=lambda h: h.position)
    assert [h.text for h in headers] == ["항목", "2023", "2024E"]

    # Check rows and cells
    assert len(table.rows) == 2
    rows = sorted(table.rows, key=lambda r: r.position)
    
    # First row
    row1_cells = sorted(rows[0].cells, key=lambda c: c.position)
    assert [c.text for c in row1_cells] == ["매출액", "100", "120"]
    
    # Second row
    row2_cells = sorted(rows[1].cells, key=lambda c: c.position)
    assert [c.text for c in row2_cells] == ["영업이익", "10", "15"]

def test_store_tables(session, sample_table_data):
    """여러 테이블 저장 테스트"""
    storer = TableStorer(session)
    tables = storer.store_tables([sample_table_data, sample_table_data])
    
    assert len(tables) == 2
    for table in tables:
        assert table.company == "삼성전자"
        assert len(table.headers) == 3
        assert len(table.rows) == 2
