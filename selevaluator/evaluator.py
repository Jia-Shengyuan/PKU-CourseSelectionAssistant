import asyncio
from selevaluator.agent.llm import LLM, LLM_Settings, AsyncLLM, LLM_Response
from selevaluator.agent.logger.logger import Logger
from typing import List
from rich.markdown import Markdown
from pathlib import Path
from api.models.chat import EvaluateRequest, GenPlanRequest, TreeholeSearchRequest
from string import Template

class RawComment: 

    evaluation_template = Template(
'''
你是一个帮助大学生汇总网络平台上课程评价的AI助手，需要通过以下信息汇总出课程评价：
1. 课程名称
2. 从学校的匿名网络平台“树洞”上搜索得到的原始课程评价
3. 本学期开课的老师列表

根据这些信息，你需要先总体简单介绍一下这门课程，然后再按老师风评从优到劣的顺序对老师进行排序，并给出对每位老师的具体评价。
课程及老师的介绍可以从给分好坏，任务量，课程难度，教学质量，以及其他你认为重要的方面进行。最终的评价需要简短，但也不能丢失任何有用的细节。

需要注意：
1. 由于原始评价通过网络平台直接搜索获取，其中可能会包含网络用语（如使用拼音首字母代指词汇），你需要注意识别。
2. 原始信息中会包含无关信息，你需要忽略这些信息，只关注课程和老师的评价。
3. 你最终给出的评价中，只需包含本学期开课的老师，不要包含未开课的老师。而如果某个本学期开课的老师未被提到，请直接输出"xxx：未找到评价"（其中xxx为老师姓名）。
4. 有一些课程有实验班。你可以认为实验班和非实验班几乎是两门课，因此对非实验班的老师进行评价时，不要考虑实验班，反之亦然（当然，如果有评价直接对比了实验班和非实验班的老师，你也可以在课程介绍中适当加入）。
5. 有一些课程只有一个老师开课。在这种情况下，你不必再对老师进行单独的评价，而是将老师评价和课程评价融入在一起输出。
6. 由于你的输出会直接影响用户的决策，因此评价中不好的方面你可以直接说出，不必委婉。
7. 你的输出必须严格基于给出的搜索结果，严禁自行编造。
8. 不要使用Markdown。

你需要评价的课程是 ${course_name}，这门课本学期开课的老师有 ${teachers}。
从网络平台上搜索到的原始评价是：
${comment}
'''
)

    def __init__(self, course_name = '', teachers = '', comment = ''):
        
        self.course_name = course_name
        self.teachers = teachers
        self.comment = comment

        # according to https://docs.siliconflow.cn/cn/userguide/capabilities/reasoning
        # we should avoid using the "system" role, and use "user" role instead
        self.messages = [
            {
                "role": "user", 
                "content": RawComment.evaluation_template.substitute(
                    course_name=course_name, teachers=teachers, comment=comment
                )
            },
            {"role": "user", "content": "请根据以上信息，为我生成课程评价。"}
        ]

    def get_query(self):
        return self.messages

class Evaluator:

    def __init__(self, request : EvaluateRequest, display_while_running : bool = False, model_name = "Pro/deepseek-ai/DeepSeek-V3"):
        # remove duplicates from request.choices, join as string
        teachers = ', '.join(sorted({t for t in request.choices if t}))
        self.course = RawComment(course_name = request.course_name, teachers = teachers, comment = request.raw_text)
        self.display_while_running = display_while_running
        self.model = request.model
        self.model_name = model_name

    async def evaluate(self):

        # If evaluation already exists, just read from file
        file_path = Path("selevaluator/data") / f"{self.course.course_name}.txt"
        if file_path.exists():
            content = str()
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            if content and content.strip():
                yield content
                return
        
        logger = Logger()
        settings = LLM_Settings(model_name=self.model.name, temperature=self.model.temperature, top_p=self.model.top_p, model_type="evaluate")
        llm = AsyncLLM(settings, logger)

        messages = self.course.messages

        try:

            response_generator = llm.chat(messages)
            full_response = ""

            if self.display_while_running:
                logger.log("AI回复: ")

            async for token in response_generator:

                if self.display_while_running:
                    logger.log(token, end="")  # 实时打印

                if token.state == "error":
                    yield f"[ERROR] {token.content}"
                    return
                
                # Evaluation only returns the final result
                if token.state == "answering":
                    full_response += token.content
                    yield token.content

            if self.display_while_running:
                logger.log("")  # 打印换行
            

        except Exception as e:
            logger.log_error(e)
            yield f"[ERROR] 发生错误：{e}"
            return

        # logger.log_info("\nResult:")
        # logger.log(Markdown(full_response))
        file_path = Path("selevaluator/data") / f"{self.course.course_name}.txt"  # 自动处理路径分隔符
        with open(file_path, 'w', encoding='utf-8') as file:
            # if (len(full_response) > 100):
            file.write(full_response)
        return

