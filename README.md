# 주식 분석 테이블 추출 및 처리

주식 분석 PDF 보고서에서 테이블을 추출하고 정제/구조화하는 파이썬 라이브러리입니다.

## 요구사항

- Python 3.8 이상
- Claude API 키

## 설치 방법

1. 가상 환경 생성:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate   # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. Claude API 키 설정:
```bash
# .env 파일 생성
ANTHROPIC_API_KEY=your_api_key_here
```

## 프로젝트 구조

```
src/
├── models.py               # 공통 데이터 모델
├── extraction/           # 테이블 추출 모듈
│   ├── __init__.py
│   └── extractor.py       # Claude API 기반 추출 로직
└── processing/          # 테이블 처리 모듈
    ├── __init__.py
    └── processor.py       # 데이터 정제 및 구조화 로직

tests/
├── extraction/          # 추출 모듈 테스트
└── processing/         # 처리 모듈 테스트
```

## 기능 설명

### 1. 테이블 추출 (extraction)

PDF 파일에서 테이블을 자동으로 추출합니다.

```python
from datetime import date
from src.extraction.extractor import TableExtractor

extractor = TableExtractor()

# PDF에서 테이블 추출
tables = extractor.extract_tables("path/to/20240101-samsung-kiwoom.pdf")
```

### 2. 테이블 처리 (processing)

추출된 테이블 데이터를 정제하고 구조화된 형태로 변환합니다.

#### 주요 기능

- 테이블 헤더 정제
  - 불필요한 공백 제거
  - 줄바꿈 처리
  - 필수 문자 보존 (알파벳, 숫자, (), %, 배)
- 셀 데이터 정제
  - 불필요한 공백 제거
  - 빈 값 처리 (-, N/A)
  - 줄바꿈 처리
- 메타데이터 관리 (파일명, 기업명, 증권사, 보고서 일자 등)

#### 사용 예시

```python
from datetime import date
from src.processing.processor import TableProcessor
from src.models import TableMetadata

# 메타데이터 설정
metadata = TableMetadata(
    file_name="20240101-samsung-kiwoom.pdf",
    company="samsung",
    securities_firm="kiwoom",
    report_date=date(2024, 1, 1),
    page_number=1
)

# 원본 테이블 데이터 예시
raw_table = {
    "page_number": 1,
    "description": "분기별 실적",
    "headers": ["항목", "Q1", "Q2", "Q3", "Q4"],
    "rows": [
        ["항목 1", "1,234", "2,345", "3,456", "4,567"],
        ["항목 2", "5,678", "6,789", "7,890", "8,901"]
    ]
}

# 테이블 처리
processor = TableProcessor()
processed_table = processor.process_table(raw_table, metadata)
```

## 테스트

모든 테스트 실행:
```bash
python -m pytest
```

특정 모듈 테스트:
```bash
python -m pytest tests/extraction/  # 추출 모듈 테스트
python -m pytest tests/processing/  # 처리 모듈 테스트
```

통합 테스트 (외부 API 호출 포함):
```bash
python -m pytest -m integration
```

### 다음 단계

1. 저장 (storage)
   - SQLite 데이터베이스 스키마 설계
   - SQLModel을 사용한 ORM 구현
   - 테이블 데이터 영구 저장

2. 검색 (retrieval)
   - FastAPI 기반 REST API 구현
   - 테이블 검색 및 필터링 기능
   - 데이터 포맷팅 및 변환 옵션
