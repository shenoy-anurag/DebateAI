from typing import Optional
import uuid
from pathlib import Path

import config
from rag.pipeline import RAGPipeline


class UploadService:
    _sessions: dict[str, dict] = {}

    @classmethod
    def process_upload(cls, file_path: Path, file_name: str) -> str:
        session_id = str(uuid.uuid4())
        
        pipeline = RAGPipeline()
        chunk_count = pipeline.process_and_store(
            file_path=file_path,
            session_id=session_id,
            paper_title=file_name
        )
        
        cls._sessions[session_id] = {
            "file_name": file_name,
            "chunk_count": chunk_count,
            "session_id": session_id
        }
        
        return session_id

    @classmethod
    def get_session(cls, session_id: str) -> Optional[dict]:
        return cls._sessions.get(session_id)

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        if session_id in cls._sessions:
            pipeline = RAGPipeline()
            pipeline.delete_session(session_id)
            del cls._sessions[session_id]
            return True
        return False
