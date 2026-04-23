from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.rag.embedder import embed_text


async def hybrid_search(
    db: AsyncSession,
    query: str,
    elements: list[str],
    context_types: list[str],
    top_k: int = 5,
) -> list[dict]:
    """
    벡터 유사도 검색 + 메타데이터 필터 조합
    elements로 1차 필터 → 벡터 검색으로 2차 정렬
    """
    query_embedding = await embed_text(query)

    sql = text("""
        SELECT
            id,
            category,
            content,
            elements,
            context,
            1 - (embedding <=> :embedding::vector) AS similarity
        FROM saju_knowledge
        WHERE
            (elements && :elements::text[] OR context && :contexts::text[])
        ORDER BY
            embedding <=> :embedding::vector
        LIMIT :top_k
    """)

    result = await db.execute(sql, {
        "embedding": str(query_embedding),
        "elements": elements,
        "contexts": context_types,
        "top_k": top_k,
    })

    return [
        {
            "id": row.id,
            "category": row.category,
            "content": row.content,
            "similarity": float(row.similarity),
        }
        for row in result.fetchall()
    ]


async def simple_search(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """필터 없이 벡터 유사도만으로 검색 (fallback)"""
    query_embedding = await embed_text(query)

    sql = text("""
        SELECT
            id,
            category,
            content,
            1 - (embedding <=> :embedding::vector) AS similarity
        FROM saju_knowledge
        ORDER BY embedding <=> :embedding::vector
        LIMIT :top_k
    """)

    result = await db.execute(sql, {
        "embedding": str(query_embedding),
        "top_k": top_k,
    })

    return [
        {
            "id": row.id,
            "category": row.category,
            "content": row.content,
            "similarity": float(row.similarity),
        }
        for row in result.fetchall()
    ]
