"""공유 LLM 싱글턴 및 RAG 헬퍼"""

from langchain_openai import ChatOpenAI
from app.rag.retriever import hybrid_search, simple_search
from app.core.database import get_db_session
from app.core.config import settings

_llm: ChatOpenAI | None = None
_structured_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.7,
            streaming=True,
            api_key=settings.OPENAI_API_KEY,
        )
    return _llm


def get_structured_llm() -> ChatOpenAI:
    """structured output 전용 — streaming 없이 안정적으로 JSON 파싱"""
    global _structured_llm
    if _structured_llm is None:
        _structured_llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.7,
            streaming=False,
            api_key=settings.OPENAI_API_KEY,
        )
    return _structured_llm


async def rag(query: str, elements: list[str], contexts: list[str], top_k: int = 4) -> str:
    """RAG 하이브리드 검색 결과를 문자열로 반환 (실패 시 빈 문자열)"""
    try:
        async with get_db_session() as db:
            results = await hybrid_search(
                db=db,
                query=query,
                elements=elements,
                context_types=contexts,
                top_k=top_k,
            )
        return "\n\n".join(f"[{r['category']}] {r['content']}" for r in results[:3])
    except Exception:
        return ""


async def rag_simple(query: str, top_k: int = 4) -> str:
    """RAG 단순 검색 결과를 문자열로 반환 (실패 시 빈 문자열)"""
    try:
        async with get_db_session() as db:
            results = await simple_search(db=db, query=query, top_k=top_k)
        return "\n\n".join(f"[{r['category']}] {r['content']}" for r in results[:3])
    except Exception:
        return ""
