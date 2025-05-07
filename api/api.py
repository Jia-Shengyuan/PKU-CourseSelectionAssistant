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
from app.db.session import SessionLocal
from scripts.search_in_pdf import extract_courses_from_pdf
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
    db = SessionLocal()

    print("Get course request : " + str(course_request))

    # Fake search results
    

@app.post("/course/plan")
async def fetch_course_by_plan(fetch_request: FetchCourseByPlanRequest) -> List[Course]:
    """
    Fetch course by plan, given semester, grade and plan_path.
    """

    # Return fake results
    course_names = extract_courses_from_pdf(fetch_request.plan_path, fetch_request.grade, fetch_request.semester) 

@app.post("/chat")
async def chat(chat_request: str) -> StreamingResponse:
    """
    Chat with LLM.
    """
    pass
