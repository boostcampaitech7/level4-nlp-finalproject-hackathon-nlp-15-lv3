from fastapi import APIRouter
from utils import RetrievalItem, RetrievalOutput

router = APIRouter()

@router.post("/retrieve")
async def retrieval(item: RetrievalItem) -> RetrievalOutput:
    dummy_documents = [
        {
            "id": "doc1",
            "text": "4Q24 예상 영업이익을 기존 8.1조원에서 7.9조원으로...",
            "metadata": {},
            "score": 0.9
        },
        # ...
    ]
    
    return RetrievalOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        related_documents=dummy_documents
    )