from typing import Generator, Union
import re
import asyncio
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from utils import ChatItem, RagItem, StreamingResponse
from services.llm import get_llm, get_memory
from .rag import rag

# Remove the prefix as it's handled in the main router
router = APIRouter()

@router.post("/", response_model=None)  # Changed from "/chat" to "/"
async def chat(
    item: ChatItem,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
) -> Union[str, FastAPIStreamingResponse]:
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
        Union[FastAPIStreamingResponse, Response]: 대화 작업 결과
    """
    result = await rag(
        RagItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=item.messages[-1].content,
        ),
        llm=llm,
        memory=memory
    )

    contents = re.split("( )", result.answer)

    if not item.stream:
        return Response(content="".join(contents), media_type="text/plain")

    async def generate_response() -> Generator:
        for content in contents:
            yield content
            await asyncio.sleep(0.02)

    return FastAPIStreamingResponse(
        generate_response(),
        media_type="text/plain"
    )