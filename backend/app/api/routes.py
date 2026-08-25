from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.api import ConversationResponse, MessageRequest
from app.services import conversation_service
from app.services.conversation_service import SessionNotFoundError

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "SOPĀNA API"}


@router.post("/conversation/start", response_model=ConversationResponse)
def start_conversation() -> ConversationResponse:
    try:
        result = conversation_service.start_conversation()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not start conversation: {exc}") from exc
    return ConversationResponse(**result)


@router.post("/conversation/message", response_model=ConversationResponse)
def send_message(payload: MessageRequest) -> ConversationResponse:
    if not payload.message.strip() and not payload.selected_options:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        result = conversation_service.send_message(payload.session_id, payload.message, payload.selected_options)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not process message: {exc}") from exc
    return ConversationResponse(**result)


@router.get("/profile/{session_id}")
def get_profile(session_id: str) -> dict:
    try:
        return conversation_service.get_profile(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc


@router.get("/learning-path/{session_id}")
def get_learning_path(session_id: str) -> dict:
    try:
        path = conversation_service.get_learning_path(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    if path is None:
        raise HTTPException(status_code=404, detail="Learning path not generated yet for this session.")
    return path


@router.get("/skill-gap/{session_id}")
def get_skill_gap(session_id: str) -> dict:
    try:
        gap = conversation_service.get_skill_gap(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    if gap is None:
        raise HTTPException(status_code=404, detail="Skill gap not computed yet for this session.")
    return gap


@router.post("/learning-path/{session_id}/steps/{step_id}/start")
def start_learning_step(session_id: str, step_id: str) -> dict:
    try:
        return conversation_service.start_learning_step(session_id, step_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/learning-path/{session_id}/steps/{step_id}/complete")
def complete_learning_step(session_id: str, step_id: str) -> dict:
    try:
        return conversation_service.complete_learning_step(session_id, step_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/dashboard/{session_id}")
def get_dashboard(session_id: str) -> dict:
    try:
        dashboard = conversation_service.get_dashboard(session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Unknown session_id.") from exc
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not available yet for this session.")
    return dashboard
