from fastapi import APIRouter, Depends
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests
import logging

from models import RetrievalItem, RagItem, RagOutput, RetrievalOutput
from services.llm import get_llm, get_memory
from core.config import settings
from utils.prompts import WEB_RAG_TEMPLATE 

logger = logging.getLogger(__name__)
router = APIRouter()

async def perform_web_search(item: RetrievalItem) -> RetrievalOutput:
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
    related_documents = await perform_web_search(
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

    prompt = PromptTemplate(
        input_variables=["history", "context", "query"],
        template=WEB_RAG_TEMPLATE
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