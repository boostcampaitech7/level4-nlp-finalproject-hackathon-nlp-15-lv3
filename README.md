# 📕 프로젝트 개요: 증권사 자료 기반 주식 LLM 서비스 개발

- **프로젝트 목표**: PDF 문서로부터 유용한 정보를 추출하고, 이를 기반으로 주식 관련 질의에 대해 정확한 답변을 제공하는 LLM 서비스 개발
- **핵심 기능**:
  - PDF 문서에서 텍스트 및 그래프 등 정보 추출
  - 데이터 레포지토리 구축 (GraphDB, VectorDB 등 활용)
  - 쿼리에 대해 최적의 데이터를 찾는 RAG 시스템 구현
  - 프롬프트 엔지니어링 및 답변 생성
  - Q&A 기능을 통한 정량 평가 수행
  
## 😁 팀 소개
<table style="width: 100%; text-align: center;">
  <tr>
    <th><a href="https://github.com/member1">팀원 1</a></th>
    <th><a href="https://github.com/member2">팀원 2</a></th>
    <th><a href="https://github.com/member3">팀원 3</a></th>
    <th><a href="https://github.com/member4">팀원 4</a></th>
    <th><a href="https://github.com/member5">팀원 5</a></th>
  </tr>
</table>

## 📆 세부 일정
- 프로젝트 기간: 2025.1.10 ~ .2.12

## 프로젝트 주요 모듈
- **PDF 정보 추출**: 텍스트 및 그래프 등 핵심 정보 파싱
- **데이터베이스 구축**: GraphDB, VectorDB를 활용한 효율적 데이터 저장 및 검색
- **RAG (Retrieval-Augmented Generation) 시스템**: 적절한 문서 검색 및 최적의 답변 생성
- **프롬프트 엔지니어링**: 효과적인 질의 응답을 위한 프롬프트 설계
- **REST API 구현**: 질의 입력 시 답변을 제공하는 API 서비스 구축

## 프로젝트 아키텍처
- PDF Parser → embedding/VectorDB → RAG System → LLM → REST API

## 평가 기준
### (필수)
1. **정량 평가 (50%)**: 테스트셋 질의에 대한 답변 성능 평가 (G-Eval 등 활용)
2. **정성 평가 (50%)**: 서비스 창의성, 유용성, 개발 완성도, 소스코드 품질 및 문서화 수준

## 프로젝트 결과
### Baseline
(결과 이미지 추가 예정)

### Mid
(결과 이미지 추가 예정)

### Final
(결과 이미지 추가 예정)

## Usage
### Requirements
```bash
pip install -r requirements.txt
```

### Command
```bash
cd ./stock_llm_service/src
python run.py
```

# Appendix
## 개발 환경
### 하드웨어
- **서버**: 실험 및 학습을 위한 GPU 서버 활용
  - GPU: NVIDIA A100 40GB
  - Storage: 200GB SSD

### 소프트웨어
- **Python 3.10**
- **PyTorch 2.X**
- **HuggingFace Transformers**
- **LangChain**
- **DVC**
- **FastAPI**
- **Jupyter Notebook**

### 협업 및 프로젝트 관리 도구
- **GitHub**: 코드 버전 관리 및 협업. GitHub Flow 활용.
- **Notion**: 프로젝트 문서화 및 일정 관리.
- **Slack & Zoom**: 팀 내 소통 및 회의 진행.
- **pre-commit**: 코드 스타일 및 품질 유지.

