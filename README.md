# 주식 분석 테이블 추출

주식 분석 PDF 보고서에서 테이블을 추출하고 처리합니다.

## 설치

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

3. Claude API 키를 포함한 `.env` 파일 생성:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## 프로젝트 구조

- `src/table_extraction/`: 테이블 추출 메인 모듈
  - `models.py`: 테이블과 메타데이터를 위한 데이터 모델
  - `extractor.py`: Claude를 사용한 테이블 추출 핵심 로직

## 사용법

(구현 후 추가 예정)
