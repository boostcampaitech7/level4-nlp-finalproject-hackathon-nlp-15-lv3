from fastapi import APIRouter
from utils import IndexingItem, IndexingOutput

router = APIRouter()

@router.post("/indexing")
async def indexing(item: IndexingItem) -> IndexingOutput:
    return IndexingOutput(
        id=item.id,
        name=item.name,
        group_id=item.group_id,
        is_success=True
    )