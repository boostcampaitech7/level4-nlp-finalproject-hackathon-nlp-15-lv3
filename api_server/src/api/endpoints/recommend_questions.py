from typing import Union
import logging
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory

from utils import ChatItem
from services.llm import get_llm

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=None)
async def recommend_questions(
    item: ChatItem,
    llm: ChatGoogleGenerativeAI = Depends(get_llm)
) -> Union[Response, StreamingResponse]:
    """다음 질문 추천 기능을 제공합니다."""
    
    query = item.messages[-1].content
    logger.info(f"[recommend_questions] Chat messages:\n\n{query}")

    prompt_template = """
    질문과 다음 정보들을 참고하여 5가지 후속 질문을 추천하도록 한다.
    기업, 종목, 주식, 주가, 주주 가치 제고, 향후 전망에 대한 질문이어도 좋고 아니어도 좋다.
    관련하여 세계 경제에 대한 질문이어도 좋고 아니어도 좋다.
    생각하지 못한 관점 또는 창의적인 관점에서 질문 5가지를 추천하도록 한다.
    각 질문은 한 문장으로 구성되어 간결하면서도 그럼에도 직관적이어야 한다.
    양식은 질문 앞에 @ 특수기호를 붙여서 각 질문을 구분할 수 있도록 한다.

    질문: {query}

    추천 질문:
    """

    prompt = PromptTemplate(
        input_variables=["query"],
        template=prompt_template
    )

    qa_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    result = qa_chain.run({"query": query})

    if not item.stream:
        return Response(content=result, media_type="text/plain")

    async def generate_response():
        for chunk in result.split():
            yield f"{chunk} "

    return StreamingResponse(
        generate_response(),
        media_type="text/plain"
    )