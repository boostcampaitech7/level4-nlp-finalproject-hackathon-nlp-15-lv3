# 주식 분석 테이블 추출/처리/저장

주식 분석 PDF 보고서의 테이블 처리를 담당하는 모듈입니다. PDF에서 테이블을 추출하고, 정제/구조화하여 데이터베이스에 저장합니다.

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
├── extraction/            # 테이블 추출 모듈
│   ├── __init__.py
│   └── extractor.py       # Claude API 기반 추출 로직
├── processing/            # 테이블 처리 모듈
│   ├── __init__.py
│   └── processor.py       # 데이터 정제 및 구조화 로직
└── storage/              # 테이블 저장 모듈
    ├── __init__.py
    └── storer.py         # SQLite 저장 로직

tests/
├── extraction/           # 추출 모듈 테스트
├── processing/          # 처리 모듈 테스트
└── storage/             # 저장 모듈 테스트
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

### 3. 테이블 저장 (storage)

추출되고 처리된 테이블을 SQLite 데이터베이스에 저장합니다.

#### 데이터베이스 스키마

- `Table` - 테이블 메타데이터 (파일명, 회사명, 증권사, 보고서 날짜, 페이지 번호)
- `TableHeader` - 테이블 헤더 정보 (텍스트, 위치)
- `TableRow` - 테이블 행 정보 (위치)
- `TableCell` - 테이블 셀 데이터 (텍스트, 위치)

#### 사용 방법

```python
from src.storage import init_db, get_session
from src.storage.storer import TableStorer

# 데이터베이스 초기화
init_db()

# 세션 생성
with next(get_session()) as session:
    # 테이블 저장
    storer = TableStorer(session)
    stored_table = storer.store_table(table_data)
```

저장된 테이블은 `data/tables.db` SQLite 파일에서 확인할 수 있습니다.

## 테스트

모든 테스트 실행:
```bash
python -m pytest
```

특정 모듈 테스트:
```bash
python -m pytest tests/extraction/    # 추출 모듈 테스트
python -m pytest tests/processing/   # 처리 모듈 테스트
python -m pytest tests/storage/      # 저장 모듈 테스트
```

통합 테스트 (외부 API 호출 포함):
```bash
python -m pytest -m integration
```

### 다음 단계

1. 검색 (retrieval)
   - 저장된 테이블 검색 API 구현
   - 테이블 검색 및 필터링 기능
   - 데이터 포맷팅 및 변환 옵션
