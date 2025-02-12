from fastapi import APIRouter, Depends
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import requests
import logging

from models import RetrievalItem, RagItem, RagOutput, RetrievalOutput
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