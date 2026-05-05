"""사주 API 엔드포인트

POST /saju/calculate   → 사주팔자 계산 (기존 유지)
POST /saju/session     → 전체 분석 SSE 스트림 (신규, 9화면 앱용)
POST /saju/chat        → 채팅 SSE 스트림 (신규, thread_id 기반)

기존 /analyze, /analyze/stream 도 하위 호환 유지.
"""

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.engine.models import (
    SajuAnalysisRequest,
    SajuRequest,
    FullAnalysisRequest,
    AnalyzeRequest,
    ChatRequest,
)
from app.engine.calculator import calculate_saju
from app.agent.graph import get_graph

router = APIRouter(prefix="/saju", tags=["사주"])


# ── 사주 계산 (기존 유지) ─────────────────────────────────────────────────────

@router.post("/calculate")
async def get_saju_calculation(request: SajuRequest):
    """사주팔자 계산만 반환"""
    saju_data = calculate_saju(request)
    return {"success": True, "data": saju_data}


# ── 전체 분석 세션 (신규) ─────────────────────────────────────────────────────

@router.post("/session")
async def start_session(request: FullAnalysisRequest):
    """
    9화면 사주 앱 — 전체 분석 SSE 스트림

    SSE 이벤트 순서:
      event: saju_data    → 만세력 데이터 (JSON)
      event: personality  → 기질·성격 분석 텍스트
      event: yearly       → 올해 운세 텍스트
      event: monthly      → 이번 달 운세 (JSON dict: {총운, 연애운, 재물운, 직업운, 사업운})
      event: timeline     → 4개월 타임라인 (JSON list: [{year, month, month_label, month_pillar, summary, highlight, highlight_content}, ...])
      event: answer       → 질문 답변 텍스트 (question 있을 때만)
      event: done         → {"thread_id": "..."} 완료
      event: error        → 오류 메시지
    """
    thread_id = str(uuid.uuid4())

    async def generate():
        graph = get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "birth_date":    request.birth_date,
            "birth_time":    request.birth_time or "미상",
            "gender":        request.gender,
            "calendar_type": request.calendar_type,
            "city":          request.city,
            "name":          request.name,
            "relationship":  request.relationship,
            "question":      request.question,
            "saju_data":     None,   # None → calculate → personality → yearly → monthly
            "messages":      [],
        }

        try:
            async for chunk in graph.astream(initial_state, config):
                # calculate 노드 완료 → 만세력 데이터
                if "calculate" in chunk and chunk["calculate"].get("saju_data"):
                    payload = json.dumps(chunk["calculate"]["saju_data"], ensure_ascii=False)
                    yield f"event: saju_data\ndata: {payload}\n\n"

                # personality 노드 완료 → 기질·성격 분석
                elif "personality" in chunk:
                    text = chunk["personality"].get("personality_analysis") or ""
                    yield f"event: personality\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

                # yearly 노드 완료
                elif "yearly" in chunk:
                    text = chunk["yearly"].get("yearly_fortune") or ""
                    yield f"event: yearly\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

                # monthly 노드 완료 → dict (5개 카테고리)
                elif "monthly" in chunk:
                    data = chunk["monthly"].get("monthly_fortune") or {}
                    yield f"event: monthly\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

                # timeline 노드 완료 → 4개월 타임라인 리스트
                elif "timeline" in chunk:
                    data = chunk["timeline"].get("timeline_fortune") or []
                    yield f"event: timeline\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

                # question 노드 완료 (질문 있을 때만)
                elif "question" in chunk:
                    text = chunk["question"].get("question_answer") or ""
                    if text:
                        yield f"event: answer\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

            yield f"event: done\ndata: {json.dumps({'thread_id': thread_id})}\n\n"

        except Exception as exc:
            yield f"event: error\ndata: {json.dumps(str(exc), ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── 채팅 (신규) ───────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    기존 세션에 채팅 메시지 전송 — SSE 토큰 스트림

    체크포인트에서 이전 분석 결과를 복원한 뒤
    사용자 메시지에 대해 스트리밍으로 응답합니다.

    SSE 형식:
      data: <token>
      data: [DONE]
    """
    async def generate():
        graph = get_graph()
        config = {"configurable": {"thread_id": request.thread_id}}

        # 사용자 메시지만 추가 — 나머지 state는 체크포인트에서 복원
        chat_state = {
            "messages": [HumanMessage(content=request.message)],
        }

        try:
            sent_done = False
            async for event in graph.astream_events(chat_state, config, version="v2"):
                kind = event.get("event", "")

                # LLM 스트리밍 토큰
                if kind == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    if not chunk:
                        continue
                    content = getattr(chunk, "content", None)
                    if isinstance(content, str) and content:
                        yield f"data: {content}\n\n"
                    elif isinstance(content, list):
                        for part in content:
                            text = part.get("text", "") if isinstance(part, dict) else (part if isinstance(part, str) else "")
                            if text:
                                yield f"data: {text}\n\n"

                # 그래프 실행 완료
                elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                    if not sent_done:
                        sent_done = True
                        yield "data: [DONE]\n\n"

            if not sent_done:
                yield "data: [DONE]\n\n"

        except Exception as exc:
            yield f"data: [ERROR] {exc}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── 2단계 AI 분석 (만세력·오행 확인 후 호출) ──────────────────────────────────

@router.post("/analyze")
async def analyze_with_saju(request: AnalyzeRequest):
    """
    사전 계산된 saju_data를 받아 AI 운세 분석만 실행.
    saju_data 있음 + messages 없음 → personality → yearly → monthly → [question]

    SSE 이벤트 순서:
      event: personality → 기질·성격 분석 텍스트
      event: yearly      → 올해 운세 텍스트
      event: monthly     → 이번 달 운세 (JSON dict: {총운, 연애운, 재물운, 직업운, 사업운})
      event: timeline    → 4개월 타임라인 (JSON list)
      event: answer      → 질문 답변 텍스트 (question 있을 때만)
      event: done        → {"thread_id": "..."} 완료
      event: error       → 오류 메시지
    """
    thread_id = str(uuid.uuid4())

    async def generate():
        graph = get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        # saju_data 있음 + messages 빈 리스트 → route_start가 "personality"로 라우팅
        initial_state = {
            "saju_data":     request.saju_data,
            "name":          request.name,
            "gender":        request.gender,
            "birth_date":    request.birth_date,
            "birth_time":    request.birth_time or "미상",
            "calendar_type": request.calendar_type,
            "relationship":  request.relationship,
            "question":      request.question,
            "messages":      [],
        }

        try:
            async for chunk in graph.astream(initial_state, config):
                if "personality" in chunk:
                    text = chunk["personality"].get("personality_analysis") or ""
                    yield f"event: personality\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

                elif "yearly" in chunk:
                    text = chunk["yearly"].get("yearly_fortune") or ""
                    yield f"event: yearly\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

                elif "monthly" in chunk:
                    data = chunk["monthly"].get("monthly_fortune") or {}
                    yield f"event: monthly\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

                elif "timeline" in chunk:
                    data = chunk["timeline"].get("timeline_fortune") or []
                    yield f"event: timeline\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

                elif "question" in chunk:
                    text = chunk["question"].get("question_answer") or ""
                    if text:
                        yield f"event: answer\ndata: {json.dumps(text, ensure_ascii=False)}\n\n"

            yield f"event: done\ndata: {json.dumps({'thread_id': thread_id})}\n\n"

        except Exception as exc:
            yield f"event: error\ndata: {json.dumps(str(exc), ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── 하위 호환 엔드포인트 ───────────────────────────────────────────────────────

_LEGACY_STATE = {
    "saju_data":       None,
    "ohaeng_analysis": None,
    "yearly_fortune":  None,
    "monthly_fortune": None,
    "question_answer": None,
    "messages":        [],
    "name":            "",
    "relationship":    "",
}


@router.post("/analyze/legacy")
async def analyze_saju(request: SajuAnalysisRequest):
    """하위 호환 — 단일 LLM 분석 응답"""
    thread_id = str(uuid.uuid4())
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    # question_type 매핑 (기존 타입 → question 필드)
    question = request.question or ""
    if request.question_type == "팔자":
        question = question or "사주팔자를 분석해주세요."
    elif request.question_type == "세운":
        question = question or "올해 운세를 분석해주세요."
    elif request.question_type == "월운":
        question = question or "이번 달 운세를 분석해주세요."

    state = {
        **_LEGACY_STATE,
        "birth_date":    request.birth_date,
        "birth_time":    request.birth_time,
        "gender":        request.gender,
        "calendar_type": request.calendar_type,
        "question":      question,
    }

    result = await graph.ainvoke(state, config)
    answer = (
        result.get("question_answer")
        or result.get("monthly_fortune")
        or result.get("yearly_fortune")
        or result.get("ohaeng_analysis")
        or ""
    )
    return {"success": True, "saju_data": result.get("saju_data"), "answer": answer}


@router.post("/analyze/stream")
async def analyze_saju_stream(request: SajuAnalysisRequest):
    """하위 호환 — 스트리밍 SSE (단순 텍스트)"""
    thread_id = str(uuid.uuid4())

    async def generate():
        graph = get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        question = request.question or ""
        if request.question_type == "팔자":
            question = question or "사주팔자를 분석해주세요."
        elif request.question_type == "세운":
            question = question or "올해 운세를 분석해주세요."
        elif request.question_type == "월운":
            question = question or "이번 달 운세를 분석해주세요."

        state = {
            **_LEGACY_STATE,
            "birth_date":    request.birth_date,
            "birth_time":    request.birth_time,
            "gender":        request.gender,
            "calendar_type": request.calendar_type,
            "question":      question,
        }

        async for event in graph.astream_events(state, config, version="v2"):
            if event.get("event") == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield f"data: {chunk.content}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
