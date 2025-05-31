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
class Course(BaseModel):
    name: str
    class_id: int # ??? who changed it to float?
    course_id: str
    note: Optional[str] = None
    time: Optional[str] = None
    credit: Optional[float] = 0
    teacher: Optional[str] = None
    location: Optional[str] = None
'''
#每个功能拆成函数
def single_course_info(evaluated_course : list[Course]) -> str:
    info = f'''
学分 = {evaluated_course.choices[0].credit}
课程可选的老师有
{' '.join(each_course.teacher + "课程id是:" + each_course.course_id + '\n课程时间是' + each_course.time for each_course in evaluated_course.choices)}
'''
    return info
async def generate_single_plan(data : GenPlanRequest, display : bool = False):
    logger = Logger()
    settings = LLM_Settings()
    llm = LLM(settings, logger)
    ChosenCourses =[]
    all_classes = data.all_classes.copy()
    all_classes = [c.course_name + '评价:' + c.summary + single_course_info(c) for c in all_classes]
    # 不同role content 信息重要性是否不同
    request = f'''
    用户提供以下课程作为本学期的课程备选,
    根据课程的评价, 选择课表中的课程, 并选择最合适老师和时间, 注意上课时间不要重叠
    
    学分范围, 最低{data.min_credits} 最高{data.max_credits}
    用户的需求:{data.class_choosing_preference}
    {'\n'.join(all_classes)}
    培养方案:'  {data.plan} 

'''

    if display == True:
        logger.log(request, end="")
    messages = [{"role": "system", "content": '''你是一个AI助手，请从用户提供的课程中选择合适的课程排布课表。
                最终只需要返回两行, 第一行是选择的每个课程的id和时间,
                格式:不同课程之间使用'|'分割 课程的不同时间用','分割,课程id和时间之间用':'分割 例如4834260:all,1,5-6;odd,4,7-8;|4834210:all,2,1-2;
                其中时间格式: 每个课程可能有一个或多个时间段构成 每个时间段三部分: 之间用','分开 
                 第一部分从以下三个词中选择:每周上课all 单周上课odd 双周上课even 
                 第二部分是上课的星期, 从1 2 3 4 5 6 7 中选择
                 第三部分是当天第几节上课 由两个数字用-连接组成 例如 1-2, 7-9, 8-12
                第二行是选择这个课表的理由
整体回复例如:
4834260:all,2,3-4;all,4,7-8|4834200:all,5,5-6;all,2,5-6|4834210:all,1,3-4;all,4,5-6|4830220:all,2,7-8;odd,4,3-4|4830145:all,1,5-6
选择的理由：
1. 优先选择了核心必修课程（操作系统、编译原理、计算机网络）和重要选修课程（数据库概论、计算机组织与 体系结构实习），满足优秀毕业生要求中的至少选修三门核心课程的条件
2. 所有课程时间安排没有冲突，且分布在一周的不同时间段，便于学生合理安排学习时间
3. 总学分为20分（4+4+4+3+2+3），满足20-24学分的范围要求
4. 选择了评价较高的老师授课的课程，如陈向群教授的操作系统课程等，保证教学质量
5. 课程组合涵盖了系统结构与并行计算类组、软件系统类组等多个类别，满足专业选修课的分类要
 '''}]
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
    list_of_id_and_time = full_response.split('|')
    for txt in list_of_id_and_time: #需要一些确保稳定性的判断
        class_id, time_str = list_of_id_and_time.split(':')
        class_id = int(class_id)
        ChosenCourses #待补充
    return ChosenCourses
