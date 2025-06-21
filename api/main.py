from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import os
import shutil
from datetime import datetime
from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.chat import EvaluateRequest, GenPlanRequest, TreeholeSearchRequest
from api.models.config import ConfigData, CONFIG_PATH
from api.output.excel_exporter import export_to_excel
# from api.models.crawler import TreeholeDriver
from crawler.driver import TreeholeDriver
from typing import List, Dict, Any
from selevaluator.agent.llm import AsyncLLM, LLM_Response
from selevaluator.agent.settings import LLM_Settings
from selevaluator.evaluator import RawComment, Evaluator
from selevaluator.selector import generate_single_plan
from selevaluator.agent.logger import Logger
from db.interface import activate_database_, get_course_info_, read_pdf_plan_, fetch_course_by_plan_
import os
from crawler.search_courses import search_treehole
# from selevaluator import selector
''' I think this may be the entrance of this project.'''

app = FastAPI()

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.post("/course/upload_plan_pdf")
async def set_plan_pdf(file: UploadFile = File(...)) -> dict:
    """
    Upload plan pdf file and save it to config/plan.pdf
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只接受PDF文件")
            
        # 确保目录存在
        os.makedirs("config", exist_ok=True)
        file_path = "config/plan.pdf"
        
        # 删除已存在的文件（如果有）
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # 保存上传的文件 - 使用完整读取再写入的方式
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
            
        return {"success": True, "message": "培养方案PDF上传成功"}
    except Exception as e:
        print(f"上传培养方案PDF失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传培养方案PDF失败: {str(e)}")
    
@app.get("/course/has_plan_pdf")
async def has_plan_pdf() -> bool:
    """
    Check if the plan pdf exists.
    """
    return os.path.exists("config/plan.pdf")

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
    print("Logging in to treehole...")
    try:
        driver = TreeholeDriver()
        driver.login()
    except Exception as e:
        error_msg = str(e)
        if "cannot find Chrome binary" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="Chrome浏览器未安装或未正确配置。请确保已安装Chrome浏览器并重试。"
            )
        elif "ChromeDriver" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="ChromeDriver配置错误。请检查网络连接，ChromeDriver将自动下载。"
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"浏览器启动失败：{error_msg}"
            )

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
    Search treehole by course_name, and return the result, including all specified teachers.
    """
    print(f"teachers = {search_request.teachers} for course {search_request.course_name}")
    try:
        course = search_request.course_name
        teachers = search_request.teachers
        html_content = f"<html><body><h1>{course}</h1>"
        print("teachers：")
        for element in teachers:
            print(element)
        html_content = await asyncio.to_thread(
            search_treehole, course, teachers, html_content, search_request.max_len, 1, 0.5
        )
        html_content += "</body></html>"
        return html_content

    except Exception as e:
        print(f"搜索课程评价失败: {e}")
        raise


@app.post("/llm/evaluate")
async def evaluate(evaluate_request: EvaluateRequest) -> StreamingResponse:
    """
    Evaluate the course by class_name and raw_text.
    """
    E = Evaluator(evaluate_request, display_while_running=False)
    return StreamingResponse(
        E.evaluate(),
        media_type="text/plain"
    )

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
async def gen_test_plan(gen_plan_request: GenPlanRequest) -> StreamingResponse:

    print(gen_plan_request)

    fake_courses = [
        [
            Course(name="数学分析II", class_id=1, course_id="1", time="all,1,3-4;all,3,1-2;", teacher="lwg", credit=5),
            Course(name="高等代数II", class_id=2, course_id="2", time="all,2,3-4;all,5,1-2;", teacher="wfz", credit=4)
        ],
        [
            Course(name="爱基础", class_id=3, course_id="3", time="all,1,5-6;odd,4,7-8;", teacher="dh", credit=3)
        ]
    ]
    
    async def gen_fake_result():
        think = ["这是一个模拟的思考过程\n", "我将输出测试用的假课表"]
        for item in think:
            yield json.dumps({
                "type": "reasoning",
                "state": "reasoning",
                "content": item
            }, ensure_ascii=False) + "\n"
            await asyncio.sleep(0.5)

        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"output/课表_{timestamp}.xlsx"
        export_to_excel(fake_courses, filename)  # 导出到Excel文件

        yield json.dumps({
            "type": "result",
            "data": [[course.model_dump() for course in plan] for plan in fake_courses]
        }, ensure_ascii=False) + "\n"

    return StreamingResponse(
        gen_fake_result(),
        media_type="application/x-ndjson"
    )

@app.post("/llm/plan_stream_")
async def gen_plan_stream(gen_plan_request: GenPlanRequest) -> StreamingResponse:
    """
    生成选课方案，使用流式响应返回推理过程和最终结果。
    支持实时显示推理过程和最终的选课结果。
    """
    async def generate_plans():
        async for item in generate_single_plan(gen_plan_request, display=True):
            if isinstance(item, LLM_Response):

                # If error, return error message to user
                if item.state == "error":
                    yield json.dumps({
                        "type": "error",
                        "message": item.content
                    }, ensure_ascii=False) + "\n"
                    return
                
                # 推理过程中的chunk，返回JSON格式
                yield json.dumps({
                    "type": "reasoning",
                    "state": item.state,
                    "content": item.content
                }, ensure_ascii=False) + "\n"
            else:
                os.makedirs("output", exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"output/课表_{timestamp}.xlsx"
                export_to_excel(item, filename) # 导出到Excel文件
                # 最终的选课结果，返回JSON格式
                yield json.dumps({
                    "type": "result",
                    "data": [[course.model_dump() for course in plan] for plan in item]
                }, ensure_ascii=False) + "\n"

    return StreamingResponse(
        generate_plans(),
        media_type="application/x-ndjson"
    )

@app.post("/llm/plan")
async def gen_plan(gen_plan_request: GenPlanRequest) -> List[List[Course]]:
    """
    生成选课方案，返回一个List[List[Course]]，表示所有选课方案。
    其中每个List[Course]表示一组选课方案。
    """
    async for item in generate_single_plan(gen_plan_request, display=False):
        if not isinstance(item, LLM_Response):
            # 只返回最终的选课结果，忽略推理过程
            return item
    
    # 如果没有得到结果，返回空列表
    return []

# 挂载静态文件服务（用于生产环境）
# 必须在所有API路由定义之后，确保API路由优先级更高
ui_dist_path = "ui/dist"
if os.path.exists(ui_dist_path):
    app.mount("/", StaticFiles(directory=ui_dist_path, html=True), name="static")
