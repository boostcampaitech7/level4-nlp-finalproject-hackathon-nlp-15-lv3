from fastapi import APIRouter, Depends
from langchain.prompts import PromptTemplate

from models import RagItem, RagOutput, RetrievalItem
from core.config import settings
from services.retrieval import search_in_chromadb
from services.llm import get_llm, get_memory
from utils.prompts import RAG_TEMPLATE, CHAT_TEMPLATE

import logging
import time
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/")
async def rag(
    item: RagItem,
    llm = Depends(get_llm)
) -> RagOutput:
    try:
        # load conversation history
        memory = get_memory(item.id)
        
        # Add delay before making the LLM call
        time.sleep(1)  # 1 second delay
        
        searched_docs = search_in_chromadb(
            query=item.query,
            collection_name=settings.collection_name,
            top_k=item.top_k
        )

        query = item.query
        context = ""
        content = ""

        # 검색 결과가 있을 경우 유사도 필터링 적용
        if searched_docs and searched_docs.related_documents:
            # 각 문서의 유사도 점수 로깅
            for i, doc in enumerate(searched_docs.related_documents):
                logger.info(f"Document {i + 1} similarity score: {doc.score:.4f}")
                logger.debug(f"Document {i + 1} text preview: {doc.text[:100]}...")

            #FIXME: find proper score to filter
            filtered_docs = [
                doc for doc in searched_docs.related_documents 
                if doc.score >= 0.0005
            ]
            
            if filtered_docs:
                logger.info(f"Selected {len(filtered_docs)} documents with scores >= 0.8:")
                for i, doc in enumerate(filtered_docs):
                    logger.info(f"Selected document {i + 1} score: {doc.score:.4f}")
                
                context = "\n\n".join(doc.text for doc in filtered_docs) 
                content = "{context}\n\n{query}".format(context=context, query=query)
                prompt_template = RAG_TEMPLATE
            else:
                logger.info("No documents passed similarity threshold (>= 0.8) switching to chat mode")
                context = ""
                prompt_template = CHAT_TEMPLATE
        else:
            # 검색 결과가 없는 경우
            context = ""  # 컨텍스트 비우기
            prompt_template = CHAT_TEMPLATE
            logger.info("No search results found, using chat mode")

        messages = item.messages[:-1] + [{"role": "user", "content": content or query}]

        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [rag] Chat messages:\n\n{messages}")
        
        prompt = PromptTemplate(
            input_variables=["history", "context", "query"],
            template=prompt_template,
        )

        # Create a runnable sequence
        chain = prompt | llm

        # Use invoke with appropriate context
        result = chain.invoke({
            "history": memory.buffer,
            "context": context,
            "query": query
        })

        return RagOutput(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            answer=result.content if hasattr(result, 'content') else str(result),
            context=context
        )

    except Exception as e:
        logger.error(f"RAG 처리 중 오류 발생: {str(e)}")
        return RagOutput(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            answer="서비스 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            context=""
        )
