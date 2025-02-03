import pytest
from datetime import date
from decimal import Decimal

from src.models import TableMetadata, TableData
from src.processing.processor import TableProcessor

@pytest.fixture
def processor():
    return TableProcessor()

@pytest.fixture
def sample_metadata():
    return TableMetadata(
        file_name="20240101-samsung-kiwoom.pdf",
        company="samsung",
        securities_firm="kiwoom",
        report_date=date(2024, 1, 1),
        page_number=1
    )

def test_clean_header(processor):
    """헤더 정제 테스트"""
    cases = [
        ("매출액(억원)", "매출액(억원)"),
        ("영업이익\n(YoY%)", "영업이익 (YoY%)"),
        ("PER (배) ", "PER (배)"),
        ("!@#마진율$%^", "마진율%"),
    ]
    
    for input_text, expected in cases:
        assert processor.clean_header(input_text) == expected

def test_clean_cell(processor):
    """셀 데이터 정제 테스트"""
    cases = [
        ("1,234.5", "1,234.5"),
        ("-", ""),
        ("N/A", ""),
        ("  12.3%  ", "12.3%"),
        ("5조 3,000억", "5조 3,000억"),
    ]
    
    for input_text, expected in cases:
        assert processor.clean_cell(input_text) == expected

def test_process_table(processor, sample_metadata):
    """전체 테이블 처리 테스트"""
    raw_table = {
        "page_number": 1,
        "description": "주요 재무지표",
        "headers": ["구분", "매출액(억원)", "영업이익(억원)", "순이익(억원)"],
        "rows": [
            ["2023", "5조 3,000억", "1조 2,000억", "8,000억"],
            ["2022", "4조 8,000억", "1조 1,000억", "7,500억"]
        ]
    }
    
    result = processor.process_table(raw_table, sample_metadata)
    
    assert isinstance(result, TableData)
    assert len(result.headers) == 4
    assert len(result.rows) == 2
    assert result.metadata.page_number == 1
    assert result.notes == "주요 재무지표"
    assert result.rows[0][1] == "5조 3,000억"  # Check a specific cell
