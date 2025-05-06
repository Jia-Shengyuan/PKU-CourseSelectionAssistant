from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.config import ConfigData, CONFIG_PATH
from typing import List, Dict, Any
from src.agent.llm import AsyncLLM
from src.agent.settings import LLM_Settings
import os

''' I think this may be the entrance of this project.'''

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

@app.get("/config")
async def get_config() -> ConfigData:
    """
    获取配置文件内容
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return ConfigData(**config)
    except Exception as e:
        print(f"Error reading config: {e}")
        raise

@app.post("/config")
async def save_config(config: ConfigData):
    """
    保存配置文件内容
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        # 写入文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, ensure_ascii=False, indent=4)
        return {"message": "配置保存成功"}
    except Exception as e:
        print(f"Error saving config: {e}")
        raise


@app.post("/course/info")
async def get_course_info(course_request: CourseSearchRequest) -> List[Course]:

    """
    Get course info from database by course_name and class_id, or course_name and teacher.
    If class_id and teacher is both not provided, then get all courses by course_name.
    """

    # Fake database
    database = [
        Course(name="数学分析", class_id=1, teacher="lpd", credit=5, time="1-2节", location="理教101", course_id="1234567890"),
        Course(name="数学分析", class_id=2, teacher="lwg", credit=5, time="3-4节", location="理教102", course_id="1234567891"),
        Course(name="高等代数", class_id=1, teacher="wfz", credit=4, time="1-2节", location="二教103", course_id="1234567890"),
        Course(name="高等代数", class_id=2, teacher="lww", credit=4, time="3-4节", location="二教104", course_id="1234567891"),
        Course(name="恨基础", class_id=2, teacher="dh", credit=3, time="5-6节", location="二教105", course_id="1234567892"),
    ]

    print("Get course request : " + str(course_request))

    # Fake search results
    filtered_courses = filter(lambda x: x.name == course_request.name, database)
    if course_request.class_id is not None:
        filtered_courses = filter(lambda x: x.class_id == course_request.class_id, filtered_courses)
    if course_request.teacher is not None:
        filtered_courses = filter(lambda x: x.teacher == course_request.teacher, filtered_courses)

    return list(filtered_courses)

@app.post("/course/plan")
async def fetch_course_by_plan(fetch_request: FetchCourseByPlanRequest) -> List[Course]:
    """
    Fetch course by plan, given semester, grade and plan_path.
    """

    # Return fake results
    database = [
        Course(name="数学分析", class_id=1, teacher="lpd", credit=5, time="1-2节", location="理教101", course_id="1234567890"),
        Course(name="数学分析", class_id=2, teacher="lwg", credit=5, time="3-4节", location="理教102", course_id="1234567891"),
        Course(name="高等代数", class_id=1, teacher="wfz", credit=4, time="1-2节", location="二教103", course_id="1234567890"),
        Course(name="高等代数", class_id=2, teacher="lww", credit=4, time="3-4节", location="二教104", course_id="1234567891"),
        Course(name="恨基础", class_id=2, teacher="dh", credit=3, time="5-6节", location="二教105", course_id="1234567892"),
    ]
    return database

@app.post("/chat")
async def chat(chat_request: str) -> StreamingResponse:
    """
    Chat with LLM.
    """
    pass
