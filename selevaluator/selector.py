from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.chat import GenPlanRequest, EvaluatedCourse
import asyncio
from selevaluator.agent.llm import LLM, LLM_Settings, AsyncLLM
from selevaluator.agent.logger.logger import Logger
from typing import List
from rich.markdown import Markdown
from pathlib import Path
'''
class GenPlanRequest(BaseModel):
    all_classes: List[EvaluatedCourse] # 每门课为一项
    user_description: str
    plan: str # 培养方案
    class_choosing_preference: str
    min_credits: int
    max_credits: int
    num_plans: int = 1 # 生成多少个选课计划
class EvaluatedCourse(BaseModel):
    course_name: str
    summary: str # LLM对课程的总结
    choices: List[Course] # 待选课程列表
'''
async def generate_single_plan(data : GenPlanRequest, display : bool = False):
    logger = Logger()
    settings = LLM_Settings()
    llm = LLM(settings, logger)
    ChosenCourses =[[Course(name="数学分析", class_id=1, course_id="3", teacher="lwg"),
             Course(name="高等代数", class_id=1, course_id="2", teacher="wfz")],
            [Course(name="恨基础", class_id=2, course_id="2", teacher="dh")]]
    classes = data.all_classes
    classes = [c.course_name + '评价:' + c.summary for c in classes]
    # 不同role content 信息重要性是否不同
    request = f'''
    用户提供以下课程作为本学期的课程备选,
    根据课程的评价, 选择课表中的课程, 并选择老师和可选时间
    {'\n'.join(classes)}
    '''
    request += '培养方案:' + data.plan

    messages = [{"role": "system", "content": "你是一个AI助手，请从用户提供的课程中选择合适的课程排布课表。"}]
    try:
        messages.append({"role": "user", "content": request})
        response = llm.chat(messages)
            
        full_response = ""
        if display == True:
            logger.log("AI回复: ")

        for token in response:
            if display == True:
                logger.log(token, end="")
            full_response += token
    except Exception as e:
        logger.log_error(e)
    return ChosenCourses
