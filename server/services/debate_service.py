from typing import Dict, Optional, List
import uuid

from services.upload_service import UploadService
from agents.topic_generator import TopicGeneratorWithRAG, DebateTopic
from agents.manager import DebateManager, DebateState, DebateStatus
from agents.debate_agent import DebateTurn


class DebateService:
    _sessions: Dict[str, DebateState] = {}

    @classmethod
    def create_session(
        cls,
        session_id: str,
        topic: str,
        pro_premise: str,
        con_premise: str
    ) -> DebateManager:
        manager = DebateManager(
            session_id=session_id,
            topic=topic,
            pro_premise=pro_premise,
            con_premise=con_premise
        )
        
        cls._sessions[session_id] = manager.get_state()
        return manager

    @classmethod
    def get_session(cls, session_id: str) -> Optional[DebateState]:
        return cls._sessions.get(session_id)

    @classmethod
    def start_debate(cls, session_id: str) -> DebateTurn:
        manager = DebateManager(
            session_id=session_id,
            topic=cls._sessions[session_id].topic,
            pro_premise=cls._sessions[session_id].pro_premise,
            con_premise=cls._sessions[session_id].con_premise
        )
        
        turn = manager.start()
        cls._sessions[session_id] = manager.get_state()
        
        return turn

    @classmethod
    def next_turn(cls, session_id: str) -> Optional[DebateTurn]:
        if session_id not in cls._sessions:
            return None
        
        state = cls._sessions[session_id]
        
        manager = DebateManager(
            session_id=session_id,
            topic=state.topic,
            pro_premise=state.pro_premise,
            con_premise=state.con_premise
        )
        
        manager.state = state
        
        next_turn_obj = manager.next_turn()
        
        should_continue = manager.should_continue()
        
        if not should_continue:
            final_response = manager.end_debate()
            state = manager.get_state()
            cls._sessions[session_id] = state
            return None
        
        cls._sessions[session_id] = manager.get_state()
        
        return next_turn_obj

    @classmethod
    def end_debate(cls, session_id: str) -> Optional[DebateState]:
        if session_id not in cls._sessions:
            return None
        
        state = cls._sessions[session_id]
        
        manager = DebateManager(
            session_id=session_id,
            topic=state.topic,
            pro_premise=state.pro_premise,
            con_premise=state.con_premise
        )
        
        manager.state = state
        manager.end_debate()
        
        cls._sessions[session_id] = manager.get_state()
        
        return manager.get_state()

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            UploadService.delete_session(session_id)
            return True
        return False
