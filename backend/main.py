from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import router
from app.agent.graph import init_graph, close_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # LangGraph + PostgreSQL 체크포인터 초기화
    await init_graph(settings.PSYCOPG_URL)
    yield
    # 커넥션 풀 정리
    await close_graph()


app = FastAPI(
    title="사주 AI Agent",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
