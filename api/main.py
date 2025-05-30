from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.chat import EvaluateRequest, GenPlanRequest, TreeholeSearchRequest
from api.models.config import ConfigData, CONFIG_PATH
# from api.models.crawler import TreeholeDriver
from crawler.driver import TreeholeDriver
from typing import List, Dict, Any
from src.agent.llm import AsyncLLM
from src.agent.settings import LLM_Settings
from db.interface import activate_database_, get_course_info_, read_pdf_plan_, fetch_course_by_plan_
import os
from crawler.search_courses import search_treehole
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
    如果config.json不存在，则从config.default.json读取默认配置并保存
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            # config/config.default.json
            default_config_path = os.path.join(os.path.dirname(CONFIG_PATH), 'config.default.json')
            if not os.path.exists(default_config_path):
                raise FileNotFoundError("默认配置文件不存在")
            
            with open(default_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        else:
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

@app.post("/course/activate")
async def activate_database(semester: str) -> None: # 需要的是形如 "2024-2025-2" 的字符串
    activate_database_(semester)


@app.post("/course/info")
async def get_course_info(course_request: CourseSearchRequest) -> List[Course]:

    """
    Get course info from database by course_name and class_id, or course_name and teacher.
    If class_id and teacher is both not provided, then get all courses by course_name.
    """

    print("Get course request : " + str(course_request))

    return get_course_info_(course_request)

@app.post("/course/plan_pdf")
async def read_pdf_plan() -> str:
    """
    Read the pdf of plan, return the overall string.
    """

    return read_pdf_plan_('config/plan.pdf')
    

@app.post("/course/plan")
async def fetch_course_by_plan(fetch_request: FetchCourseByPlanRequest) -> List[Course]: 
    """
    Fetch course by plan, given semester, grade and plan_path.
    """
    # 这里面的 semester 需要的是上/下 也可以让我这边改

    return fetch_course_by_plan_(fetch_request)

@app.post("/crawler/login")
async def treehole_login() -> None:
    """
    Login to treehole, return nothing.
    """
    # 假设你已经实现了单例(singleton)模式，后续代码可以通过static的方法get_instance()获取driver
    driver = TreeholeDriver()
    driver.login()

@app.post("/crawler/close")
async def treehole_close() -> None:
    """
    Close the treehole driver.
    """
    driver = TreeholeDriver()
    driver.close()

@app.post("/crawler/search_courses")
async def treehole_search(search_request: TreeholeSearchRequest) -> str:
    """
    Search treehole by course_name, and return the result.
    """
    try:
        course = search_request.course_name
        # 使用单例模式的driver
        # driver = TreeholeDriver.get_instance() # 假设你已经实现了单例(singleton)模式
        html_content = f"<html><body><h1>{course}</h1>"
        result = await asyncio.to_thread(search_treehole, course, html_content, search_request.max_len, 1, 0.5)
        return result
    except Exception as e:
        print(f"搜索课程评价失败: {e}")
        raise

@app.post("/llm/evaluate")
async def evaluate(evaluate_request: EvaluateRequest) -> StreamingResponse:
    """
    Evaluate the course by class_name and raw_text.
    """
    pass

@app.post("/llm/evaluate_test")
async def evaluate_test(evaluate_request: EvaluateRequest) -> StreamingResponse:
    """
    模拟流式输出，将输入的raw_text按行分割并逐行返回
    """
    async def generate_response():
        # 按行分割文本
        lines = evaluate_request.raw_text.split('\n')
        
        # 逐行返回，每行之间添加短暂延迟
        for line in lines:
            if line.strip():  # 跳过空行
                yield line + "\n"
                await asyncio.sleep(0.01)  # 每行之间暂停0.5秒

    return StreamingResponse(
        generate_response(),
        media_type="text/plain"
    )

@app.post("/llm/plan_stream")
async def gen_plan_stream(gen_plan_request: GenPlanRequest) -> StreamingResponse:
    """
    生成选课方案，使用流式响应逐个返回每个方案。
    每个方案是一个List[Course]，表示一组选课组合。
    总共会生成num_plans个方案。
    """
    async def generate_plans():
        for i in range(gen_plan_request.num_plans):
            # 这里调用大模型生成一个选课方案
            # 实际上，这些课程可能都是由同一次大模型调用生成的，所以你可以考虑和大模型约定输出格式，一次生成结束之后怎么标记一下
            plan = await generate_single_plan(gen_plan_request)  # 这个函数需要你实现
            # 将方案转换为JSON字符串并返回
            yield json.dumps(plan, ensure_ascii=False) + "\n"
            # 可选：在方案之间添加短暂延迟
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate_plans(),
        media_type="application/x-ndjson"  # 使用newline-delimited JSON格式
    )

@app.post("/llm/plan")
async def gen_plan(gen_plan_request: GenPlanRequest) -> List[List[Course]]:
    """
    生成选课方案，返回一个List[List[Course]]，表示所有选课方案。
    其中每个List[Course]表示一组选课方案。
    """
    return [[Course(id=1, name="高等数学", teacher="张三", time="1-2节", location="东区101")]]
