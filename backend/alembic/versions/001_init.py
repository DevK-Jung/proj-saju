"""init schema

Revision ID: 001
Revises:
Create Date: 2026-04-22
"""
from typing import Sequence, Union
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.execute("""
        CREATE TABLE IF NOT EXISTS saju_knowledge (
            id          TEXT PRIMARY KEY,
            category    TEXT NOT NULL,
            elements    TEXT[] NOT NULL,
            gender      TEXT DEFAULT '공통',
            context     TEXT[] NOT NULL,
            content     TEXT NOT NULL,
            embedding   vector(1024),
            created_at  TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS saju_knowledge_embedding_idx
        ON saju_knowledge
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS saju_knowledge_elements_idx
        ON saju_knowledge USING GIN(elements)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS saju_knowledge_context_idx
        ON saju_knowledge USING GIN(context)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS saju_knowledge_content_fts_idx
        ON saju_knowledge USING GIN(to_tsvector('simple', content))
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS user_saju_cache (
            id              BIGSERIAL PRIMARY KEY,
            birth_date      DATE NOT NULL,
            birth_time      TEXT NOT NULL,
            gender          TEXT NOT NULL,
            calendar_type   TEXT NOT NULL,
            saju_data       JSONB NOT NULL,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(birth_date, birth_time, gender, calendar_type)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_saju_cache")
    op.execute("DROP TABLE IF EXISTS saju_knowledge")
