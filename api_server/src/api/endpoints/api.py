from typing import Generator, Union
import re
import asyncio
import json
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse, JSONResponse
from utils import ApiRequest, RagItem, ApiResponse
from services.llm import get_llm, get_memory
from .rag import rag

router = APIRouter()

@router.post("/", response_model=ApiResponse)
async def api(
    request: ApiRequest,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
) -> Union[JSONResponse, FastAPIStreamingResponse]:
    """챗봇 대화 API"""
    
    result = await rag(
        RagItem(
            id="chat",
            name="chat",
            group_id="chat",
            query=request.query,
            top_k=request.top_k
        ),
        llm=llm,
        memory=memory
    )

    response_data = ApiResponse(
        context=result.context.split("\n\n") if result.context else [],
        answer=result.answer
    )

    if not request.stream:
        return JSONResponse(content=response_data.dict())

    async def generate_response() -> Generator:
        yield json.dumps({
            "context": response_data.context,
            "answer": ""
        }) + "\n"
        
        contents = re.split("( )", result.answer)
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