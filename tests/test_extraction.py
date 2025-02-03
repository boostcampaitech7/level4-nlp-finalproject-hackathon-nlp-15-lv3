import os
import pytest
from datetime import date
from src.table_extraction import TableExtractor

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def test_metadata_parsing():
    extractor = TableExtractor()
    metadata = extractor._parse_filename("20241120-CJ제일제당-신한투자증권.pdf")
    
    assert metadata.company == "CJ제일제당"
    assert metadata.securities_firm == "신한투자증권"
    assert str(metadata.report_date) == "2024-11-20"

def test_table_extraction():
    """Test table extraction with a real stock analysis PDF"""
    extractor = TableExtractor()
    
    # Get first PDF from data directory
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        pytest.skip("No PDF files found in data directory")
    
    pdf_path = os.path.join(DATA_DIR, pdf_files[0])
    tables = extractor.extract_tables(pdf_path)
    assert isinstance(tables, list)
    assert len(tables) > 0, "Should extract at least one table"
    
    # Check first table structure
    first_table = tables[0]
    assert len(first_table.headers) > 0, "Table should have headers"
    assert len(first_table.rows) > 0, "Table should have data rows"
    assert first_table.metadata.page_number > 0, "Page number should be set"

@pytest.mark.integration
def test_real_pdf_extraction():
    """Test table extraction with a real PDF file"""
    extractor = TableExtractor()
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        pytest.skip("No PDF files found in data directory")
    
    pdf_path = os.path.join(DATA_DIR, pdf_files[0])
    
    # Basic validation
    tables = extractor.extract_tables(pdf_path)
    assert len(tables) > 0, "Should extract at least one table"
    
    # Check first table
    first_table = tables[0]
    assert first_table.metadata.company is not None
    assert first_table.metadata.securities_firm is not None
    assert first_table.metadata.report_date is not None
    assert first_table.metadata.page_number > 0, "Page number should be set"
    
    # Check table structure
    assert len(first_table.headers) > 0, "Table should have headers"
    assert len(first_table.rows) > 0, "Table should have data rows"
