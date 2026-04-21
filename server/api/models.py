from typing import Optional, List
from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    file_name: str
    chunk_count: int


class DebateTopicRequest(BaseModel):
    session_id: str


class TopicData(BaseModel):
    topic: str
    pro_premise: str
    con_premise: str


class TopicsResponse(BaseModel):
    session_id: str
    topics: List[TopicData]


class StartDebateRequest(BaseModel):
    session_id: str
    topic: str
    pro_premise: str
    con_premise: str


class DebateTurnResponse(BaseModel):
    role: str
    content: str
    citations: List[str]
    turn_number: int


class EndDebateResponse(BaseModel):
    status: str
    summary: str
    winner: str
    turns: List[DebateTurnResponse]


class DebateStatusResponse(BaseModel):
    session_id: str
    topic: str
    status: str
    current_turn: int
    winner: Optional[str] = None
    summary: Optional[str] = None
