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
# llm = AsyncLLM(LLM_Settings())

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
    Get course info from database by course_name and class_id, or course_name and teacher.
    If class_id and teacher is both not provided, then get all courses by course_name.
    """

    print(course_request)

    # Fake search results
    if course_request.name == "数学分析":
        if course_request.class_id == 1:
            return [Course(name="数学分析", class_id=1, teacher="lpd", credit=5, time="1-2节", location="理教101", course_id="1234567890")]
        if course_request.class_id == 2:
            return [Course(name="数学分析", class_id=2, teacher="lwg", credit=5, time="3-4节", location="理教102", course_id="1234567891")]
    
    if course_request.name == "高等代数":
        return [Course(name="高等代数", class_id=1, teacher="wfz", credit=5, time="1-2节", location="二教103", course_id="1234567890")]
    
    return [Course(name="Not found", class_id=-1, teacher="", credit=-1, time="", location="", course_id="-1")]


@app.post("/chat")
async def chat(chat_request: str) -> StreamingResponse:
    """
    Chat with LLM.
    """
    pass
