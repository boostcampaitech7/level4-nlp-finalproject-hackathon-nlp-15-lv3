import os
import json
import base64
import requests
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from .models import TableData, TableMetadata

class TableExtractor:
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
        date_str, company, securities_firm = filename.replace('.pdf', '').split('-')
        return TableMetadata(
            file_name=filename,
            company=company,
            securities_firm=securities_firm,
            report_date=datetime.strptime(date_str, '%Y%m%d').date(),
            page_number=0  # Will be updated during extraction
        )
    
    def _extract_tables_with_claude(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Use Claude to extract tables from PDF"""
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        data = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract all tables from this PDF. For each table, provide the following in JSON format:
{
    "page_number": int,
    "description": string,
    "headers": list[string],
    "rows": list[list[string]]
}

Notes:
1. page_number: The page where the table appears
2. description: A brief description of what the table represents
3. headers: Column headers of the table
4. rows: Data rows, where each row is a list of strings

Return the list of tables as a JSON array."""
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
            }]
        }
        
        # Make request with retries
        max_retries = 3
        retry_delay = 1  # seconds
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=data)
                if response.status_code == 529:  # Overloaded
                    if attempt < max_retries - 1:
                        print(f"Claude is overloaded, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise e
        
        # Extract JSON from Claude's response
        response_data = response.json()
        message = response_data.get('content', [{}])[0].get('text', '')
        print("Claude's response:", message)

        # Find JSON in the response
        try:
            # Extract JSON array
            start = message.find('[')
            if start == -1:
                raise ValueError("No JSON array found in response")

            # Find matching closing bracket
            stack = []
            i = start
            while i < len(message):
                if message[i] == '[':
                    stack.append('[')
                elif message[i] == ']':
                    stack.pop()
                    if not stack:  # Found matching closing bracket
                        end = i + 1
                        break
                i += 1
            else:
                raise ValueError("No matching closing bracket found")

            json_str = message[start:end]
            print("Extracted JSON:", json_str)
            tables = json.loads(json_str)

            # Convert rows to dictionary format
            for table in tables:
                headers = table['headers']
                rows = []
                for row_data in table['rows']:
                    row = {}
                    for i, value in enumerate(row_data):
                        if i == 0:  # First column is the row name
                            row['name'] = value
                        else:
                            row[headers[i-1]] = value
                    rows.append(row)
                table['rows'] = rows

            return tables
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse Claude's response: {str(e)}")
    
    def extract_tables(self, pdf_path: str) -> List[TableData]:
        """Extract all tables from a PDF file using Claude"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        base_metadata = self._parse_filename(os.path.basename(pdf_path))
        tables_json = self._extract_tables_with_claude(pdf_path)
        
        tables = []
        for table_json in tables_json:
            metadata = TableMetadata(
                file_name=base_metadata.file_name,
                company=base_metadata.company,
                securities_firm=base_metadata.securities_firm,
                report_date=base_metadata.report_date,
                page_number=table_json['page_number']
            )
            
            table = TableData(
                metadata=metadata,
                description=table_json['description'],
                headers=table_json['headers'],
                rows=table_json['rows']
            )
            tables.append(table)
        
        return tables
