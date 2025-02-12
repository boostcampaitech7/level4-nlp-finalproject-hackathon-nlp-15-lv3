from typing import Generator, Union
import re
import asyncio
import json
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse, JSONResponse
from models import ApiRequest, ApiResponse
from services.llm import get_llm
from services.retrieval import search_in_chromadb
from core.config import settings
from langchain.prompts import PromptTemplate
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ApiResponse)
async def api(
    request: ApiRequest,
    llm = Depends(get_llm)
) -> Union[JSONResponse, FastAPIStreamingResponse]:
    """챗봇 단일 질의응답 API"""
    try:
        # RAG 로직 구현
        related_documents = search_in_chromadb(
            query=request.query,
            collection_name=settings.collection_name,
            top_k=request.top_k
        )

        if not related_documents:
            return JSONResponse(content=ApiResponse(
                context=[],
                answer="검색 결과가 없습니다. 다른 질문을 해주세요."
            ).dict())

        # Context 생성
        context = "\n\n".join(doc.text for doc in related_documents.related_documents)

        # 프롬프트 템플릿 설정
        prompt_template = """        
            다음 정보들을 참고하여 중요한 내용들에 집중하여 질문에 답변한다.
            각 문맥별로 설명할 수 있는 부분을 설명한다.
            알기 힘든 주식 및 금융 용어들은 부가적으로 설명한다.
            복잡한 내용은 다시 풀어서 설명하도록 한다.
            차근차근 답변하도록 한다.
            질문과 질문 관련 내용에 집중해서 답변한다.
            사용자로부터 주어지는 정보는 질문뿐이다.
            질문 관련 내용은 이미 알고 있는 지식으로서 제공 받은 정보가 아니기 때문에 제공 받았다거나 주어진 정보라고 말하지 않는다.

            질문 관련 내용: {context}

            질문: {query}

            답변:
            """

        prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=prompt_template,
        )

        # LLM 체인 생성 및 실행
        chain = prompt | llm
        result = chain.invoke({
            "context": context,
            "query": request.query
        })

        response_data = ApiResponse(
            context=context.split("\n\n") if context else [],
            answer=result.content if hasattr(result, 'content') else str(result)
        )

        if not request.stream:
            return JSONResponse(content=response_data.dict())

        async def generate_response() -> Generator:
            yield json.dumps({
                "context": response_data.context,
                "answer": ""
            }) + "\n"
            
            contents = re.split("( )", response_data.answer)
            current_answer = ""
            for content in contents:
                current_answer += content
                yield json.dumps({
                    "context": response_data.context,
                    "answer": current_answer
                }) + "\n"
                await asyncio.sleep(0.02)

        return FastAPIStreamingResponse(
            generate_response(),
            media_type="application/x-ndjson"
        )

    except Exception as e:
        logger.error(f"API 처리 중 오류 발생: {str(e)}")
        return JSONResponse(content=ApiResponse(
            context=[],
            answer="서비스 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        ).dict())