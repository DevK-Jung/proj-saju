import asyncio
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """싱글톤으로 모델 로드 (앱 시작 시 1회만)"""
    print(f"KURE-v1 모델 로딩 중... (device={settings.EMBEDDING_DEVICE})")
    model = SentenceTransformer(
        settings.EMBEDDING_MODEL_NAME,
        device=settings.EMBEDDING_DEVICE,
    )
    print("KURE-v1 로딩 완료")
    return model


async def embed_text(text: str) -> list[float]:
    """단일 텍스트 임베딩 (CPU 블로킹 → executor 비동기 처리)"""
    loop = asyncio.get_event_loop()
    model = _get_model()
    embedding = await loop.run_in_executor(
        None,
        lambda: model.encode(text, normalize_embeddings=True).tolist()
    )
    return embedding


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """배치 임베딩 (청크 적재 시 사용)"""
    loop = asyncio.get_event_loop()
    model = _get_model()
    embeddings = await loop.run_in_executor(
        None,
        lambda: model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
    )
    return embeddings
