from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.chat import GenPlanRequest, EvaluatedCourse
import asyncio
from selevaluator.agent.llm import LLM, LLM_Settings, AsyncLLM, AgentLLM
from selevaluator.agent.logger.logger import Logger
from typing import List
from rich.markdown import Markdown
from pathlib import Path
from string import Template
import json
import re

system_template = Template(
'''
你是一个帮助大学生选课的应用中的AI助手。请根据用户提供的培养方案，课程列表，列表中课程及老师的评价，自身特点和需求，以及用户所在的年级，生成一个合理的选课计划。
请注意以下几点：
1. 如果用户有特定要求，请优先满足这些要求。如果用户特别说明的需求与后面几条矛盾，请以用户的需求为准。你需要注意用户的口吻（如是否使用了“必须”、“一定”等词语），来判断用户的需求是否是硬性要求。
2. 选课时，你需要确保培养方案中本学期的必修课都被选上（硬性要求，除非这些课程用户已经学过）。
3. 选课时，你只能选择用户提供的课程列表中的课程（硬性要求）。
4. 课程时间不能相互冲突（硬性要求）。注意，若一个课程的时间中包含多个时段，则说明这些时段都要上课（而非在其中选一个时间上），因此要保证这些时段都是不与其他课程冲突的。
5. 选择非必修课时，需要综合考虑培养方案中的学分要求，用户自身特点及未来发展，课程及教师风评，上课时间等因素。
6. 课程的学分总和需要在用户提供的学分范围内（硬性要求）。你选课的总学分，应当以用户提供的最大、最小学分的平均值为基准浮动。
7. 为早八课（即上课时间为1-2节的课程）安排相对较低的选择权重；尽量避免在某一天安排过多的课。这一条优先级相对较低。
8. 除第2条提到的本学期必修课一定要选外，你不一定需要严格按照培养方案中推荐的选课学期来选课，但需要确保这适合用户。即，如果你发现一个推荐在别的学期上的课，对这个学期的用户而言很合适，那么你可以也考虑去选。
9. 注意用户是大学生的身份，其语言中可能包含大学生的习惯性用语（如"早八"通常代指每天的第1-2节课，需要你去理解）。

用户可能需要不止一份选课计划。根据用户需要的数量，你的回复需要以json格式返回相应个数个选课计划。这些选课计划之间应该存在一些差别（例如不同的学分数，不同的课程选择等），来让用户选择采用哪个，并且你应该把你最推荐的选课计划放在最前面。每个选课计划都需要满足以上所有要求。
你可以理解成你需要以json格式回复一个List[List[Course]]，其中每个List[Course]表示一组选课方案，一个Course表示具体选的一门课。
具体而言，Course包含如下的信息：
    name: str
    class_id: int
    course_id: str
    note: Optional[str] = None
    time: Optional[str] = None
    credit: Optional[float] = 0
    teacher: Optional[str] = None
    location: Optional[str] = None

在用户提供的课程列表中，课程就会以Course的格式给出。当你想要选某门课时，你需要确保输出中除time外的其他信息都没有任何改动，而time则需要你进行如下的格式化，以方便代码对其解析：
我们用例子来说明："周一3-4节，周三1-2节" -> "all,1,3-4;all,3,1-2;"，"周二第1节" -> "all,2,1-1;"，"每周周一5-6节，单周周四7-8节" -> "all,1,5-6;odd,4,7-8;"，"双周周四10-11节" -> "even,4,10-11;"。
即，对于每门课的若干个时段，你需要将时间段之间用分号分隔，时间段的格式是"all/odd/even,星期,开始节-结束节"，其中星期从1到7分别表示周一到周日。某些课程的时间中可能包含周数（如"1-16周"或"1-9周"），但在格式化时请忽略这一信息，只按前面的要求来。
注意，由于你的输出会被程序解析，因此请确保其符合上述格式，且没有任何其他内容。

用户对自己的介绍是：${user_description}
用户对选课的额外偏好是：${class_choosing_preference}
用户希望的学分范围是${min_credits}到${max_credits}学分。
用户希望你生成${num_plans}个选课计划。

下面是用户的培养方案：${plan}

下面是课程列表，每门课包含课程名称、课程评价和具体开设的班级：${courses}
'''
)

def is_valid_time_format(time_str: str) -> bool:
    """
    检查时间字符串是否符合格式：
    "all/odd/even,星期,开始节-结束节;..."，多个时段用分号分隔，允许末尾有分号。
    例：all,1,3-4;odd,4,7-8;
    """
    if not isinstance(time_str, str):
        return False
    if time_str.strip() == '':
        return False

    full_pattern = rf"^((all|odd|even),[1-7],\d{{1,2}}-\d{{1,2}};)+$"
    return re.fullmatch(full_pattern, time_str.strip()) is not None

def remove_code_block(response: str) -> str:
    """
    移除回复中的代码块标记。
    """
    if response.startswith('```json'):
        return response.lstrip('```json').rstrip('```').strip()
    elif response.startswith('```'):
        return response.lstrip('```').rstrip('```').strip()
    return response.strip()

def parse_time_segments(time_str: str):
    """
    解析时间字符串，返回所有时段的 (week_type, weekday, start, end) 元组列表。
    """
    # if not is_valid_time_format(time_str):
        # return []
    segments = []
    for seg in time_str.strip().split(';'):
        if not seg:
            continue
        parts = seg.split(',')
        if len(parts) != 3:
            continue
        week_type, weekday, section = parts
        try:
            weekday = int(weekday)
            start, end = map(int, section.split('-'))
            segments.append((week_type, weekday, start, end))
        except Exception:
            continue
    return segments

def format_checker(response: str) -> List[str]:
    """
    检查LLM的回复是否符合预期格式。
    如果不符合，返回错误信息列表。
    """
    errors = []

    response = remove_code_block(response)
    
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        errors.append("你的回复无法被json.loads()直接解析，请确保输出符合JSON格式。")
        return errors
    
    if not isinstance(response, list):
        errors.append("你的回复应该是一个包含多个选课计划的列表，其类型应当为List[List[Course]]，但你返回的不是一个列表。")
        return errors
    
    if not all(isinstance(plan, list) for plan in response):
        errors.append("你给出的每一个选课计划都应该是一个列表，为List[Course]类型。但你返回的某些选课计划不是列表。")
        for plan in response:
            if not isinstance(plan, list):
                errors.append(f"{plan} 不是一个列表。")

        return errors

    if not all(all(isinstance(course, dict) for course in plan) for plan in response):
        errors.append("在json格式下，你给出的每一门课都应该是一个Course，对应字典类型。但你返回的某些课程不是字典类型。")
        for plan in response:
            for course in plan:
                if not isinstance(course, dict):
                    errors.append(f"{course} 不是一个字典类型。")
        return errors
    
    for plan_idx, plan in enumerate(response):
        time_table = {}  # (week_type, weekday, section) -> (course_name, class_id)
        for course in plan:

            try:
                c = Course(**course)
                if not is_valid_time_format(c.time):
                    errors.append(f"{c} 的时间格式不正确。")
                    continue

                segments = parse_time_segments(c.time)
                for week_type, weekday, start, end in segments:

                    if not (1 <= weekday <= 7):
                        errors.append(f"{c.name} 的上课星期 {weekday} 不在1~7范围内。")
                    if not (1 <= start <= 12) or not (1 <= end <= 12) or start > end:
                        errors.append(f"{c.name} 的上课节次 {start}-{end} 不在1~12范围内，或起止顺序错误。")

                    for section in range(start, end + 1):
                        key = (week_type, weekday, section)
                        if key in time_table:
                            prev_name, prev_class = time_table[key]
                            errors.append(f"选课计划{plan_idx+1}中 {c.name}(班号{c.class_id}) 与 {prev_name}(班号{prev_class}) 在 {week_type}, 星期{weekday}, 第{section}节时间冲突。请调整其中的至少一门课程。")
                        else:
                            time_table[key] = (c.name, c.class_id)

            except Exception as e:
                errors.append(f"你的回复中有课程信息不符合Course模型的要求: {e}")

    if not errors:
        return []

    return errors

async def generate_single_plan(data : GenPlanRequest, display : bool = False) -> List[List[Course]]:


    logger = Logger()
    settings = LLM_Settings()
    llm = AgentLLM(settings, logger)

    courses = json.dumps([c.model_dump() for c in data.all_classes], ensure_ascii=False)

    logger.log_info("准备生成选课计划...")

    messages = [
        {"role": "system", "content": system_template.substitute(
            plan = data.plan,
            min_credits = data.min_credits,
            max_credits = data.max_credits,
            user_description = data.user_description,
            class_choosing_preference = data.class_choosing_preference,
            num_plans = data.num_plans,
            courses = courses
        )},
        {"role": "user", "content": '请严格遵循上述要求，为我生成符合要求的选课计划。'}
    ]

    response = llm.chat(messages, error_checker=format_checker, max_retries=3)
    full_response = ""
    async for token in response:
        full_response += token

    logger.log("课表：" + full_response)
    full_response = remove_code_block(full_response)

    return [[Course(**course) for course in plan] for plan in json.loads(full_response)]

    ChosenCourses = []
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
