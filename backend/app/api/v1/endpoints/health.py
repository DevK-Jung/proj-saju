from fastapi import APIRouter

router = APIRouter(tags=["헬스체크"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "사주 AI Agent"}
