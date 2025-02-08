import re
from typing import Dict, List, Any

from src.models import TableData, TableMetadata

class TableProcessor:
    """테이블 데이터 정제 및 구조화를 담당하는 클래스"""

    def clean_header(self, header: str) -> str:
        """헤더 텍스트 정제"""
        if not header:
            return ""
            
        # 줄바꿈을 공백으로 변환
        header = ' '.join(header.split())
        
        # 특수문자 처리 (마진율% 등의 경우 보존)
        cleaned = ''
        for char in header:
            if char.isalnum() or char in '()%배 ':
                cleaned += char
        
        return cleaned.strip()

    def clean_cell(self, cell: str) -> str:
        """셀 데이터 정제"""
        if not cell:
            return ""
            
        # 빈 값 처리
        cell = cell.strip()
        if cell in ('-', 'N/A'):
            return ""
            
        # 줄바꿈 처리
        cell = ' '.join(cell.split())
        return cell.strip()

    def process_table(self, raw_table: Dict[str, Any], metadata: TableMetadata) -> TableData:
        """테이블 데이터 처리"""
        # 헤더 정제
        headers = [self.clean_header(h) for h in raw_table['headers']]
        
        # 행 데이터 정제
        rows = [[self.clean_cell(cell) for cell in row] for row in raw_table['rows']]
        
        # 테이블 데이터 생성
        return TableData(
            metadata=metadata,
            headers=headers,
            rows=rows,
            notes=raw_table.get('description', '')
        )
