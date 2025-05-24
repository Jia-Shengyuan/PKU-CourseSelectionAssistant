from pydantic import BaseModel
from typing import Optional, List
from api.models.course import Course

class TreeholeSearchRequest(BaseModel):
    course_name: str
    max_len: int = 5 # 搜多少条

class EvaluateRequest(BaseModel):
    course_name: str
    raw_text: str

# 这些 class 都是暂定的，可以按照你的需求进行修改，在群里说一声即可
class EvaluatedCourse(BaseModel):
    course_name: str
    summary: str # LLM对课程的总结
    choices: List[Course] # 待选课程列表

class GenPlanRequest(BaseModel):
    all_classes: List[EvaluatedCourse] # 每门课为一项
    user_description: str
    plan: str # 培养方案，你看是前端给你还是你自己读？
    class_choosing_preference: str
    min_credits: int
    max_credits: int
    num_plans: int = 1 # 生成多少个选课计划
