from typing import Generator, Union
import re
import asyncio
import json
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from models import ChatRequest, ChatResponse, RagItem, Utterance
from services.llm import get_llm, get_memory, conv_memories  # conv_memories 추가
from .rag import rag
from .web_rag import web_rag

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm = Depends(get_llm)
) -> Union[ChatResponse, FastAPIStreamingResponse]:
    """챗봇 대화 API"""
    
    # Load conversation memory
    memory = get_memory(request.conversation_id)
    
    # Check if load_chat option is provided
    if request.option and request.option.get("load_chat"):
        if not memory.get_user_id():  # 새로운 대화일 경우
            memory.set_user_id(request.uid)
        elif memory.get_user_id() != request.uid:  # 권한 체크
            raise HTTPException(status_code=403, detail="permission denied")
        
        messages = memory.messages  # Redis에서 메시지 이력 조회
        return ChatResponse(
            answer="",
            context=messages,
            conversation_id=request.conversation_id,
            uid=request.uid
        )
    
    # Convert Message objects to Utterance objects
    utterances = [
        Utterance(role=msg.role, content=msg.content) 
        for msg in request.messages
    ]
    
    item = RagItem(
        id=request.conversation_id,
        name=request.uid,
        group_id="chat",
        messages=utterances,
        query=request.messages[-1].content,
        top_k=request.top_k,
        stream=request.stream
    )

    # 대화 권한 체크 및 소유자 설정
    if not memory.get_user_id():
        memory.set_user_id(request.uid)
    elif memory.get_user_id() != request.uid:
        raise HTTPException(status_code=403, detail="permission denied")
    
    if request.option and request.option.get("web"):
        result = await web_rag(
            item=item,
            llm=llm,
            memory=memory
        )
    else:
        result = await rag(
            item=item,
            llm=llm,
            memory=memory
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