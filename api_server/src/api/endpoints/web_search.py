import re
from typing import Generator
import asyncio


from fastapi import APIRouter, Depends
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
import requests
import logging

from utils import RetrievalItem, RagItem, RagOutput, RetrievalOutput, ChatItem, StreamingResponse
from services.llm import get_llm, get_memory
from core.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/search")
async def web_search(item: RetrievalItem) -> RetrievalOutput:
    """웹 검색을 수행합니다."""
    query = item.query

    url = f"https://www.googleapis.com/customsearch/v1?key={settings.GOOGLE_SEARCH_API_KEY}&cx={settings.GOOGLE_CX}&q={query}"
    response = requests.get(url)
    data = response.json()
    
    docs = []
    if "items" in data:
        for i, web_item in enumerate(data['items'], start=1):
            doc = {'id':str(i), 'text': "", 'metadata': {}, 'score':1}
            if 'snippet' in web_item:
                doc['text'] = web_item['snippet']
            if 'link' in web_item:
                tmp_link = f"([link]({web_item['link']}))"
                if 'title' in web_item:
                    tmp_link = tmp_link.replace("([link]", f"([{web_item['title']}]")
                doc['text'] += tmp_link
            if 'metadata' in web_item:
                doc['metadata'] = web_item['metadata'][0]
            elif 'metatags' in web_item:
                doc['metadata'] = web_item['metatags'][0]
            
            docs += [doc]
    else:
        logger.warning("Web search results not found.")

    return RetrievalOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        related_documents=docs
    )

@router.post("/web_rag")
async def web_rag(
    item: RagItem,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
) -> RagOutput:
    """웹 검색 결과를 기반으로 RAG를 수행합니다."""
    
    # 웹 검색 수행
    related_documents = await web_search(
        RetrievalItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=item.query,
            max_query_size=item.max_query_size,
            top_k=item.top_k
        )
    )

    # 검색 결과 결합
    context = "\n\n".join(doc.text for doc in related_documents.related_documents) if related_documents.related_documents else ""

    prompt_template = """
    다음 정보들을 참고하여 중요한 내용들에 집중하여 질문에 답변한다.
    각 문맥별로 설명할 수 있는 부분을 설명한다.
    알기 힘든 주식 및 금융 용어들은 부가적으로 설명한다.
    복잡한 내용은 다시 풀어서 설명하도록 한다.
    차근차근 답변하도록 한다.
    ([title 또는 link](url))가 붙은 문장에 대해 답변을 생성할 때 해당 답변 바로 뒤에 해당 ([title 또는 link](url)) 양식 그대로 출력한다. 
    이전 대화 내용은 문맥을 파악하기 위해 참고하되 굳이 다시 언급하지 않는다.
    질문과 질문 관련 내용에 집중해서 답변한다.

    이전 대화 내용: {history}
    질문 관련 내용: {context}
    질문: {query}

    답변:
    """

    prompt = PromptTemplate(
        input_variables=["history", "context", "query"],
        template=prompt_template
    )

    qa_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    result = qa_chain.run({
        "context": context,
        "query": item.query
    })

    return RagOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        answer=result,
        context=context
    )

@router.post("/chat_web")
async def chat_web(
    item: ChatItem,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
    ):
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
    result = await web_rag(
        RagItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=item.messages[-1].content,
        ),
        llm = llm,
        memory = memory
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