from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from api.modles.course import Course, CourseSearchRequest
from typing import List
from src.agent.llm import AsyncLLM
from src.agent.settings import LLM_Settings

app = FastAPI()
llm = AsyncLLM(LLM_Settings())

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)



@app.post("/course/info")
async def get_course_info(course_request: CourseSearchRequest) -> List[Course]:
    """
    Get course info from database by course_name and class_id.
    If class_id is not provided, get all courses by course_name.
    """
    pass

@app.post("/chat")
async def chat(chat_request: str) -> StreamingResponse:
    """
    Chat with LLM.
    """
    pass
