# backend/routers/chat.py

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..services.agent_runner import run_agent_streamed
import json
from pydantic import BaseModel

class UserQuery(BaseModel):
    user_query: str

router = APIRouter()

@router.post("/run")
async def run_agent_api(request: UserQuery):

    user_input = request.user_query
    print("user input: ", user_input)

    generator = run_agent_streamed(user_input)
    print("generator response: ", generator)
    return StreamingResponse(generator, media_type="text/event-stream") # type: ignore