from fastapi import APIRouter, Depends
from langchain.chains import create_retrieval_chain, LLMChain
from langchain.prompts import PromptTemplate

from utils import RagItem, RagOutput, RetrievalItem
from services.retrieval import search_in_chromadb
from services.llm import get_llm, get_memory



router = APIRouter()

@router.post("/rag")
async def rag(
    item: RagItem,
    llm = Depends(get_llm),
    memory = Depends(get_memory)
) -> RagOutput:

    query = item.query

    '''TODO: RetrievalItem을 사용하여 관련 문서를 검색합니다.
    related_documents = await retrieval(
        RetrievalItem(
            id=item.id,
            name=item.name,
            group_id=item.group_id,
            query=query,
            max_query_size=item.max_query_size,
            top_k=item.top_k
        )
    )'''
    
    # ChromaDB에서 관련 문서 검색
    related_documents = search_in_chromadb(
        query=item.query,
        #collection_name=item.collection_name,
        top_k=item.top_k
    )

    # 검색 결과와 대화 메시지를 결합합니다.
    context = ""
    content = ""
    if related_documents.related_documents:
        context = "\n\n".join(doc.text for doc in related_documents.related_documents)
        content = "{context}\n\n{query}".format(context=context, query=query)

    '''TODO: logger 구현 
    messages = item.messages[:-1] + [{"role": "user", "content": content}]

    logger.info(f"[rag] Chat messages:\n\n{messages}")
    '''
    
    prompt_template = \
        f"""        
        다음 정보들을 참고하여 중요한 내용들에 집중하여 질문에 답변한다.
        각 문맥별로 설명할 수 있는 부분을 설명한다.
        알기 힘든 주식 및 금융 용어들은 부가적으로 설명한다.
        복잡한 내용은 다시 풀어서 설명하도록 한다.
        차근차근 답변하도록 한다.
        이전 대화 내용은 문맥을 파악하기 위해 참고하되 굳이 다시 언급하지 않는다.
        이전 대화 내용을 물어보면 같이 답변한다.
        질문과 질문 관련 내용에 집중해서 답변한다.
        사용자로부터 주어지는 정보는 질문뿐이다. 사용자는 질문 외에는 어떤 정보가 주어졌는지 알지 못하기 때문에 어떤 정보가 주어졌다고 언급하지 않는다.
        질문 관련 내용은 이미 알고 있는 지식으로서 제공 받은 정보가 아니기 때문에 제공 받았다거나 주어진 정보라고 말하지 않는다.

        이전 대화 내용 : {{history}}

        질문 관련 내용: {{context}}

        질문: {{query}}

        답변:
        """

    prompt = PromptTemplate(
        input_variables=["history", "context", "query"],
        template=prompt_template,
    )

    #qa_chain = prompt | llm
    qa_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
    )

    #qa_chain = ConversationChain(
    #    llm=llm,
    #    prompt=prompt,
    #    memory=memory
    #)

    result = qa_chain.run({
        "context": context,
        "query": query
    })

    return RagOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        answer=result,
        context=context
    )
