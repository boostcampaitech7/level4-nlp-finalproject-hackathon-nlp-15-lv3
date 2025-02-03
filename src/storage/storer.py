"""테이블 저장 모듈"""

from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path
from typing import List, Generator

from ..models import TableData, Table, TableHeader, TableRow, TableCell

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# SQLite database URL
DATABASE_URL = f"sqlite:///{DATA_DIR}/tables.db"

# Create engine
engine = create_engine(DATABASE_URL)

def init_db() -> None:
    """Initialize database and create tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session

class TableStorer:
    """테이블 저장 클래스"""

    def __init__(self, session: Session):
        self.session = session

    def store_table(self, table_data: TableData) -> Table:
        """테이블 데이터를 데이터베이스에 저장"""
        # Create table
        table = Table(
            file_name=table_data.metadata.file_name,
            company=table_data.metadata.company,
            securities_firm=table_data.metadata.securities_firm,
            report_date=table_data.metadata.report_date,
            page_number=table_data.metadata.page_number,
            notes=table_data.notes
        )
        self.session.add(table)
        
        # Create headers
        for pos, header in enumerate(table_data.headers):
            table_header = TableHeader(
                text=header,
                position=pos,
                table=table
            )
            self.session.add(table_header)
        
        # Create rows and cells
        for row_pos, row_data in enumerate(table_data.rows):
            row = TableRow(
                position=row_pos,
                table=table
            )
            self.session.add(row)
            
            # Create cells for this row
            for cell_pos, cell_text in enumerate(row_data):
                cell = TableCell(
                    text=cell_text,
                    position=cell_pos,
                    row=row
                )
                self.session.add(cell)
        
        # Commit all changes
        self.session.commit()
        self.session.refresh(table)
        
        return table

    def store_tables(self, table_data_list: List[TableData]) -> List[Table]:
        """여러 테이블 데이터를 데이터베이스에 저장"""
        return [self.store_table(table_data) for table_data in table_data_list]
