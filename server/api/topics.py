from fastapi import APIRouter, HTTPException

from api.models import DebateTopicRequest, TopicsResponse, TopicData
from services.upload_service import UploadService
from agents.topic_generator import TopicGeneratorWithRAG

router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


@router.post("/", response_model=TopicsResponse)
async def generate_topics(request: DebateTopicRequest):
    session = UploadService.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        generator = TopicGeneratorWithRAG(request.session_id)
        topics = generator.generate_topics()
        
        return TopicsResponse(
            session_id=request.session_id,
            topics=[
                TopicData(
                    topic=t.topic,
                    pro_premise=t.pro_premise,
                    con_premise=t.con_premise
                )
                for t in topics
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
