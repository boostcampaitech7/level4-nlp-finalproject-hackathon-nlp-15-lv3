import os
import json
import re
import base64
from datetime import datetime
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

from src.models import TableData, TableMetadata

class TableExtractor:
    """PDF에서 테이블을 추출하는 클래스"""

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        self.model = "claude-3-5-sonnet-latest"
    
    def _parse_filename(self, filename: str) -> TableMetadata:
        """Extract metadata from filename in format: YYYYMMDD-company-securities_firm.pdf"""
        pattern = r"(\d{8})-([^-]+)-([^.]+)\.pdf"
        match = re.match(pattern, filename)
        if not match:
            raise ValueError(f"Invalid filename format: {filename}")
            
        date_str, company, securities_firm = match.groups()
        report_date = datetime.strptime(date_str, "%Y%m%d").date()
        
        return TableMetadata(
            file_name=filename,
            company=company,
            securities_firm=securities_firm,
            report_date=report_date,
            page_number=1  # Will be updated during extraction
        )
    
    def extract_tables(self, pdf_path: str) -> List[TableData]:
        """PDF 파일에서 테이블 추출"""
        metadata = self._parse_filename(os.path.basename(pdf_path))
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        return self._extract_tables_with_claude(pdf_path)
    
    def _extract_tables_with_claude(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Claude API를 사용하여 테이블 추출"""
        system_prompt = """
        Extract all tables from the PDF and return them in the following JSON format:
        [
            {
                "page_number": int,
                "description": "Brief description or title of the table",
                "headers": ["header1", "header2", ...],
                "rows": [
                    ["row1_col1", "row1_col2", ...],
                    ["row2_col1", "row2_col2", ...],
                    ...
                ]
            },
            ...
        ]
        """
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Prepare request
        data = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all tables from this PDF and format them according to the specified JSON structure."
                        },
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            # Extract JSON from Claude's response
            message = response.json()['content'][0]['text']
            start = message.find('[')
            end = message.rfind(']') + 1
            
            if start == -1 or end == 0:
                raise ValueError("No valid JSON array found in Claude's response")
            
            tables_json = json.loads(message[start:end])
            metadata = self._parse_filename(os.path.basename(pdf_path))
            
            table_data_list = []
            for table in tables_json:
                table_metadata = metadata.model_copy()
                table_metadata.page_number = table.pop('page_number', 1)
                table['metadata'] = table_metadata
                table_data_list.append(TableData(**table))
            
            return table_data_list
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse Claude's response: {str(e)}")
        except requests.exceptions.RequestException as e:
            print(f"Response content: {response.text}")
            raise ConnectionError(f"Failed to connect to Claude API: {str(e)}")
