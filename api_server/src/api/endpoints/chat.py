from typing import Generator, Union
import re
import asyncio
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from utils import ChatRequest, RagItem, Utterance
from services.llm import get_llm, get_memory
from .rag import rag

router = APIRouter()

@router.post("/", response_model=None)
async def chat(
    request: ChatRequest,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
) -> Union[str, FastAPIStreamingResponse]:
    """챗봇 대화 API"""
    
    # Convert Message objects to Utterance objects
    utterances = [
        Utterance(role=msg.role, content=msg.content) 
        for msg in request.messages
    ]
    
    result = await rag(
        RagItem(
            id="chat",
            name="chat",
            group_id="chat",
            messages=utterances,  # Use converted utterances
            query=request.messages[-1].content,
            top_k=request.top_k
        ),
        llm=llm,
        memory=memory
    )

    contents = re.split("( )", result.answer)

    if not request.stream:
        return Response(content="".join(contents), media_type="text/plain")

    async def generate_response() -> Generator:
        for content in contents:
            yield content
            await asyncio.sleep(0.02)

    return FastAPIStreamingResponse(
        generate_response(),
        media_type="text/plain"
    )