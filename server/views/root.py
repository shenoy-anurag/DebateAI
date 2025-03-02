from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.requests import Request


router = APIRouter()


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    return {"message": "pong"}
