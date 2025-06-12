from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from api.models.chat import GenPlanRequest, EvaluatedCourse
import asyncio
from selevaluator.agent.llm import LLM, LLM_Settings, AsyncLLM, AgentLLM, LLM_Response
from selevaluator.agent.logger.logger import Logger
from typing import List, Union, AsyncGenerator
from rich.markdown import Markdown
from pathlib import Path
from string import Template
import json
import re

system_template = Template(
'''
你是一个帮助北京大学学生选课的大模型应用中的Agent。请根据用户提供的培养方案，课程列表，列表中课程及老师的评价，自身特点和需求，以及用户所在的年级，生成一个合理的选课计划。
请注意以下几点：
1. 用户的要求永远有最高的优先级。如果用户特别说明的需求与后面几条矛盾，请以用户的需求为准。
2. 选课时，你需要确保培养方案中本学期的必修课都被选上（硬性要求，除非这些课程用户已经学过）。
3. 选课时，你只能选择用户提供的课程列表中的课程（硬性要求）。
4. 任意两门课程的时间不能相互冲突（硬性要求）。即你需要保证同一时间至多有一门课。
5. 有一些核心课程（如数学课）附带习题课，上机课等。如果选了主课，则这些课程需要一并选上。
5. 选择非必修课时，需要综合考虑培养方案中的学分要求，用户自身特点及未来发展，课程及教师风评，上课时间等因素。
6. 课程的学分总和需要在用户提供的学分范围内（硬性要求）。你选课的总学分，应当以用户提供的最大、最小学分的平均值为基准浮动。
7. 每一天共有12节课，其中1-4节为上午，5-9节为下午，10-12节为晚上。你需要为早八课（即上课时间为1-2节的课程）安排相对较低的选择权重，同时尽量避免在某一天安排过多的课。
8. 除第2条提到的本学期必修课一定要选外，你不一定需要严格按照培养方案中推荐的选课学期来选课，但需要确保这适合用户。即，如果你发现一个推荐在别的学期上的课，对这个学期的用户而言很合适，那么你可以也考虑去选。

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
注意，你的输出会被Python程序用json.loads()解析。因此请确保其符合上述格式，没有任何其他内容，可以直接被程序解析。在字符串内如果要使用引号，可以使用中文的全角引号“”而不是英文的半角引号""，以避免json.loads()解析错误。

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
                        key = (weekday, section)
                        if key in time_table:
                            prev_name, prev_class = time_table[key]
                            errors.append(f"选课计划{plan_idx+1}中 {c.name}(班号{c.class_id}) 与 {prev_name}(班号{prev_class}) 在星期{weekday}, 第{section}节时间冲突。请调整其中的至少一门课程。")
                        else:
                            time_table[key] = (c.name, c.class_id)

            except Exception as e:
                errors.append(f"你的回复中有课程信息不符合Course模型的要求: {e}")

    if not errors:
        return []

    return errors

async def generate_single_plan(data : GenPlanRequest, display : bool = False) -> AsyncGenerator[Union[LLM_Response, List[List[Course]]], None]:

    logger = Logger()
    settings = LLM_Settings(model_name=data.model_name)
    llm = AgentLLM(settings, logger)

    courses = json.dumps([c.model_dump() for c in data.all_classes], ensure_ascii=False)

    logger.log_info("准备生成选课计划...")

    messages = [
        {"role": "user", "content": system_template.substitute(
            plan = data.plan,
            min_credits = data.min_credits,
            max_credits = data.max_credits,
            user_description = data.user_description,
            class_choosing_preference = data.class_choosing_preference,
            num_plans = data.num_plans,
            courses = courses
        )},
        {"role": "user", "content": '请严格遵循上述要求，为我生成符合要求的选课计划。再次强调要遵守所有的硬性需求，包括但不限于课程时间不能冲突，输出中不能对课程信息进行篡改（但要对时间信息进行格式化）等，并且确保输出中除需要的json外不包含任何其他信息。'}
    ]

    response = llm.chat(messages, error_checker=format_checker, max_retries=3)
    full_response = ""
    async for token in response:
        if token.state in ["reasoning", "retrying", "error"]:
            yield token
        elif token.state == "answering":
            full_response += token.content

    logger.log("课表：" + full_response)
    full_response = remove_code_block(full_response)

    # 最后yield选课结果
    yield [[Course(**course) for course in plan] for plan in json.loads(full_response)]
