from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from pydantic import BaseModel, EmailStr


class Query(BaseModel):
    prompt: str
    user: EmailStr


# class QueryResponse(BaseModel):
#     prompt: str
#     user: EmailStr


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", status_code=status.HTTP_200_OK, response_model=str)
async def chat(query: Query):
    print(query.user)
    print(query.prompt)
    return "Test response from LLM"
