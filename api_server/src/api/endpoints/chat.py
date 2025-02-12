from typing import Generator, Union
import re
import asyncio
import json
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from models import ChatRequest, ChatResponse, RagItem, Utterance  # ChatResponse 추가
from services.llm import get_llm, get_memory
from .rag import rag

router = APIRouter()

@router.post("/", response_model=ChatResponse)  # response_model 추가
async def chat(
    request: ChatRequest,
    llm = Depends(get_llm)
) -> Union[ChatResponse, FastAPIStreamingResponse]:
    """챗봇 대화 API"""
    
    # Convert Message objects to Utterance objects
    utterances = [
        Utterance(role=msg.role, content=msg.content) 
        for msg in request.messages
    ]
    
    result = await rag(
        RagItem(
            id=request.conversation_id,  # conversation_id 사용
            name=request.uid,            # uid를 name으로 사용
            group_id="chat",
            messages=utterances,
            query=request.messages[-1].content,
            top_k=request.top_k,
            stream=request.stream
        ),
        llm=llm
    )

    contents = re.split("( )", result.answer)

    if not request.stream:
        return ChatResponse(
            answer="".join(contents),
            context=result.context,
            conversation_id=request.conversation_id,
            uid=request.uid
        )

    async def generate_response() -> Generator:
        response_data = {
            "answer": "",
            "context": result.context,
            "conversation_id": request.conversation_id,
            "uid": request.uid
        }
        
        for content in contents:
            response_data["answer"] += content
            yield json.dumps(response_data) + "\n"
            await asyncio.sleep(0.02)

    return FastAPIStreamingResponse(
        generate_response(),
        media_type="application/x-ndjson"  # JSON Lines 형식으로 변경
    )