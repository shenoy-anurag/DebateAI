from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

import config
from api.models import UploadResponse
from services.upload_service import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = {".pdf", ".txt"}
    file_ext = file.filename[file.filename.rfind("."):].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {allowed_extensions}"
        )
    
    file_path = config.UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        session_id = UploadService.process_upload(file_path, file.filename)
        
        session = UploadService.get_session(session_id)
        
        return UploadResponse(
            session_id=session_id,
            file_name=session["file_name"],
            chunk_count=session["chunk_count"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_upload(session_id: str):
    success = UploadService.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}
