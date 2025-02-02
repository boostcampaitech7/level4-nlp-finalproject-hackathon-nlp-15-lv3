import asyncio
import logging
import os
from dotenv import load_dotenv
import re
from typing import Generator

import uvicorn
from fastapi import FastAPI
from transformers import HfArgumentParser

from langchain import hub
from langchain.chains import create_retrieval_chain, LLMChain
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models import ChatOpenAI
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

import sentence_transformers

from utils import (
    IndexingItem,
    IndexingOutput,
    RetrievalItem,
    RetrievalOutput,
    RagItem,
    RagOutput,
    ChatItem,
    StreamingResponse,
    FastApiArgument
)

logger = logging.getLogger(__name__)
parser = HfArgumentParser((FastApiArgument,))
(fastapi_args,) = parser.parse_args_into_dataclasses()
app = FastAPI()

os.environ["OPENAI_API_KEY"] = ""

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")


@app.post("/indexing")
async def indexing(item: IndexingItem) -> IndexingOutput:
    """
    문서를 입력 받아 색인(indexing) 작업을 합니다.
    Args:
        item: IndexingItem: 색인 작업을 위한 입력 데이터
            - id: str: 색인 작업을 위한 ID
            - name: str: 색인 작업을 위한 이름
            - group_id: str: 색인 작업을 위한 그룹 ID
            - documents: List[Document]: 색인할 문서 목록
            - max_chunk_size: int: 색인할 문서의 최대 chunk size
            - num_chunk_overlap: int: 색인할 문서의 chunk 간 겹치는 길이
    Returns:
        IndexingOutput: 색인 작업 결과
            - id: str: 색인 작업을 위한 ID
            - name: str: 색인 작업을 위한 이름
            - group_id: str: 색인 작업을 위한 그룹 ID
            - is_success: bool: 색인 작업 성공 여부
    """
    # TODO: 색인 작업을 수행하는 코드를 작성합니다. 현재는 성공으로 가정합니다.

    return IndexingOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        is_success=True
    )


@app.post("/retrieve")
async def retrieval(item: RetrievalItem) -> RetrievalOutput:
    """
    질의(query)를 입력 받아 검색(retrieval) 작업을 합니다.
    Args:
        item: RetrievalItem: 검색 작업을 위한 입력 데이터.
            - id: str: 검색 작업을 위한 ID.
            - name: str: 검색 작업을 위한 이름.
            - group_id: str: 검색 작업을 위한 그룹 ID.
            - query: str: 검색할 질의.
            - max_query_size: int: 검색할 질의의 최대 길이.
            - top_k: int: 검색 결과 중 상위 몇 개를 가져올지 결정. (default: 3)
    Returns:
        RetrievalOutput: 검색 작업 결과.
            - id: str: 검색 작업을 위한 ID.
            - name: str: 검색 작업을 위한 이름.
            - group_id: str: 검색 작업을 위한 그룹 ID.
            - related_documents: List[Document]: 검색 결과로 나온 문서 목록.
    """

    # TODO: 검색 작업을 수행하는 코드를 작성합니다. 현재는 고정된 결과로 가정합니다.
    """
    related_documents = [
        {
            "id": "doc1",
            "text": "This is the first document.",
            "metadata": {},
            "score": 0.9
        },
        {
            "id": "doc2",
            "text": "This is the second document.",
            "metadata": {},
            "score": 0.8
        }
    ]
    """

    dummy_documents = [
        {
            "id": "doc1",
            "text": "\
                    4Q24 예상 영업이익을 기존 8.1조원에서 7.9조원으로 소폭 하향 조정조정. 출하 증가율은 디램 +7%, 낸드 +12%로 당초 전망 을 유지하나유지하나, 가격\
                    전망을 기존 전망 대비 하향하향(기존 디램 +8%, 낸드 -5% 디램\
                    +5%, 낸드 -7%). 주된 근거는 모바일모바일, PC 등 전통 수요처 수요 부진\
                    이 기존 예상 대비 심화된 영향영향. 여전히 강한 수요가 확인되 는 AI서버\
                    시장과 대조적대조적. 지난 실적발표 컨퍼런스콜에서 레거시 재고 관련 우려\
                    에 대해 무리한 재고 소진보다 재고 캐리 계획을 언급한 바 있으나있으나, 달\
                    라진 수요 환경환경(예상대비 더욱 부진한 전통 수요와 미중 간 지정학적\
                    불확실성 등등)을 감안한 연말 재고 소진 성격의 판매가 일정 부분 동반\
                    될 수 있을 것으로 판단\
                    ",
            "metadata": {},
            "score": 0.9
        },
        {
            "id": "doc2",
            "text": "\
                    내년 예상 영업이익을 기존 31.7조원에서 29.1조원으로 하향 조정조정. AI 시장과 전통 수요처 간 수요 양극화 심화됨에 따라 가격 전망을 다소\
                    보수적으로 가정한 데 따른 것것. 당사는 내년 수요에서 변화가 없다면\
                    디램은 3Q25, 낸드는 1Q25부터 가격 하락 압력이 커질 것으로 판단\
                    ",
            "metadata": {},
            "score": 0.8
        }
    ]

    return RetrievalOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        related_documents=dummy_documents
    )

@app.post("/rag")
async def rag(item: RagItem) -> RagOutput:

    query = item.query

    related_documents = await retrieval(
        RetrievalItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=query,
            max_query_size=item.max_query_size,
            top_k=item.top_k
        )
    )

    # 검색 결과와 대화 메시지를 결합합니다.
    if related_documents.related_documents:
        context = "\n\n".join(doc.text for doc in related_documents.related_documents)
        content = "{context}\n\n{query}".format(context=context, query=query)

    messages = item.messages[:-1] + [{"role": "user", "content": content}]

    logger.info(f"[TEST] Chat messages:\n\n{messages}")

    #llm = ChatOpenAI(model="gpt-3.5-turbo")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_output_tokens=10,
        google_api_key=google_api_key
    )

    prompt_template = \
        """
        다음 정보들을 참고하여 중요한 내용들만 답변하도록 한다.
        각 문맥별로 설명할 수 있는 부분을 설명한다.
        알기 힘든 주식 및 금융 용어들은 부가적으로 설명한다.
        복잡한 내용은 다시 풀어서 설명하도록 한다.
        차근차근 답변하도록 한다.

        질문 관련 문서: {context}

        질문: {query}

        답변:
        """

    prompt = PromptTemplate(
        input_variables=["context", "query"],
        template=prompt_template,
    )

    #qa_chain = prompt | llm
    qa_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    result = qa_chain.run({
        "context": context,
        "query": query
    })

    return RagOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        answer=result,
        context=context
    )

@app.post("/chat")
async def chat(item: ChatItem):
    """
    챗봇을 위한 대화(chat) 작업을 합니다.
    Args:
        item: ChatItem: 대화 작업을 위한 입력 데이터.
            - id: str: 대화 작업을 위한 ID.
            - name: str: 대화 작업을 위한 이름.
            - group_id: str: 대화 작업을 위한 그룹 ID.
            - messages: List[Utterance]: 대화할 메시지 목록.
            - max_query_size: int: 대화할 질의의 최대 길이.
            - max_response_size: int: 대화할 응답의 최대 길이.
            - top_k: int: 검색 결과 중 상위 몇 개를 가져올지 결정. (default: 3)
            - stream: bool: 대화 작업 결과를 스트리밍할지 여부. (default: False)
    Returns:
        StreamingResponse | str: 대화 작업 결과.
            - StreamingResponse: 대화 작업 결과를 스트리밍하는 경우.
            - str: 대화 작업 결과를 한 번에 반환하는 경우.
    """

    # RAG를 수행합니다.
    result = await rag(
        RagItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=item.messages[-1].content,
        )
    )

    contents = re.split("( )", result.answer)


    # item.stream 이 False 일 경우, 한 번에 반환.
    if not item.stream:
        return "".join(contents)

    # item.stream 이 True 일 경우, StreamingResponse로 반환.
    # 현재 코드에서는 genertor를 사용하여 bytes 형태로 반환(이후 생성 모델의 스트림 출력으로 대체).
    async def generate_response() -> Generator:
        for content in contents:
            yield content
            await asyncio.sleep(0.02)

    return StreamingResponse(
        generate_response(),
        model_type="Others",
        db_manager=None,
        metadata=None
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host=fastapi_args.server_address, port=fastapi_args.server_port)
