"""pgvector 청크 적재 유틸리티"""
import asyncio
import json
from pathlib import Path
import asyncpg
from app.core.config import settings
from app.rag.embedder import embed_batch


async def ingest_from_files(chunk_dir: str = "data/chunks") -> int:
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )

    chunk_files = list(Path(chunk_dir).glob("*.json"))
    total = 0

    for chunk_file in chunk_files:
        chunks = json.loads(chunk_file.read_text(encoding="utf-8"))
        texts = [c["content"] for c in chunks]
        embeddings = await embed_batch(texts)

        for chunk, embedding in zip(chunks, embeddings):
            await conn.execute("""
                INSERT INTO saju_knowledge
                    (id, category, elements, gender, context, content, embedding)
                VALUES ($1, $2, $3, $4, $5, $6, $7::vector)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding
            """,
                chunk["id"],
                chunk["category"],
                chunk["elements"],
                chunk.get("gender", "공통"),
                chunk["context"],
                chunk["content"],
                str(embedding),
            )
        total += len(chunks)
        print(f"적재 완료: {chunk_file.name} ({len(chunks)}개)")

    await conn.close()
    return total
