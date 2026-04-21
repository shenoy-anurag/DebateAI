from fastapi import APIRouter, HTTPException

from api.models import (
    StartDebateRequest,
    DebateTurnResponse,
    DebateStatusResponse,
    EndDebateResponse
)
from services.upload_service import UploadService
from services.debate_service import DebateService

router = APIRouter(
    prefix="/debate",
    tags=["Debate"]
)


@router.post("/start")
async def start_debate(request: StartDebateRequest):
    session = UploadService.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    manager = DebateService.create_session(
        session_id=request.session_id,
        topic=request.topic,
        pro_premise=request.pro_premise,
        con_premise=request.con_premise
    )
    
    turn = DebateService.start_debate(request.session_id)
    
    return DebateTurnResponse(
        role=turn.role.value,
        content=turn.content,
        citations=[c.source or f"Page {c.page}" for c in turn.citations],
        turn_number=turn.turn_number
    )


@router.post("/next/{session_id}")
async def next_turn(session_id: str):
    state = DebateService.get_session(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Debate session not found")
    
    if state.status == "completed":
        raise HTTPException(status_code=400, detail="Debate already completed")
    
    turn = DebateService.next_turn(session_id)
    
    if turn is None:
        state = DebateService.get_session(session_id)
        return EndDebateResponse(
            status="completed",
            summary=state.summary or "",
            winner=state.winner or "tie",
            turns=[
                DebateTurnResponse(
                    role=t.role.value,
                    content=t.content,
                    citations=[c.source or f"Page {c.page}" for c in t.citations],
                    turn_number=t.turn_number
                )
                for t in state.turns
            ]
        )
    
    return DebateTurnResponse(
        role=turn.role.value,
        content=turn.content,
        citations=[c.source or f"Page {c.page}" for c in turn.citations],
        turn_number=turn.turn_number
    )


@router.get("/status/{session_id}", response_model=DebateStatusResponse)
async def get_debate_status(session_id: str):
    state = DebateService.get_session(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Debate session not found")
    
    return DebateStatusResponse(
        session_id=state.session_id,
        topic=state.topic,
        status=state.status.value,
        current_turn=state.current_turn,
        winner=state.winner,
        summary=state.summary
    )


@router.post("/end/{session_id}")
async def end_debate(session_id: str):
    state = DebateService.get_session(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Debate session not found")
    
    final_state = DebateService.end_debate(session_id)
    
    return EndDebateResponse(
        status="completed",
        summary=final_state.summary or "",
        winner=final_state.winner or "tie",
        turns=[
            DebateTurnResponse(
                role=t.role.value,
                content=t.content,
                citations=[c.source or f"Page {c.page}" for c in t.citations],
                turn_number=t.turn_number
            )
            for t in final_state.turns
        ]
    )


@router.delete("/{session_id}")
async def delete_debate(session_id: str):
    success = DebateService.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Debate session deleted successfully"}
