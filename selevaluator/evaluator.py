import asyncio
from selevaluator.agent.llm import LLM, LLM_Settings, AsyncLLM
from selevaluator.agent.logger.logger import Logger
from typing import List
from rich.markdown import Markdown
from pathlib import Path
from api.models.chat import EvaluateRequest, GenPlanRequest, TreeholeSearchRequest

class RawComment: 
    def __init__(self, course_name = '', teachers = [], comment = ''):
        self.course_name = course_name
        self.teachers = teachers
        self.comment = comment
        self.messages = [{
            "role": "user", 
            "content": f"根据评价,先总体详细介绍一下课程: {course_name}, 再从按老师从优到劣推荐课程 \
            你只用给出以下老师的具体评价: {",".join(teachers)}, \
            从给分,任务量,教学质量三个角度评价课程, 老师的名称只保留拼音缩写" 
'''
格式严格仿照以下格式
电磁字课程总体评价:
电磁学作为物理系的核心课程，内容涵盖静电场、静磁场、麦克斯韦方程组等，理论性较强但应用
泛。课程难度中等偏上，需要较好的数学基础(尤其是矢量分析和微积分)。大多数老师采用课堂讲授+作业+考试的模式，部
分老师会加入演示实验或数值模拟内容。
从往届学生反馈来看，电磁学的教学质量整体较好，但不同老师的授课风格和考核方式差异较大。
、下是按推荐程度排序的教师评价:
教师推荐(从优到劣)
(姓名)  (给分角度评价)  (任务量角度评价)  (教学质量角度评价)
沈波 给分.. 任务量.. 教学质量..
何琼毅 给分.. 任务量.. 教学质量..
''' 
" 评价:" + comment
}] 
        self.messages.append({"role": "system", "content": "你需要总结课程的评价"})
    def get_query(self):
        return self.messages

class Evaluator:
    def __init__(self, course : EvaluateRequest, display_while_running : bool = False):
        self.course = RawComment(course_name=course.course_name, comment=course.raw_text)
        self.display_while_running = display_while_running

    async def evaluate(self):
        file_path = Path("selevaluator/data") / f"{self.course.course_name}.txt"  # 自动处理路径分隔符
        if file_path.exists():
            content = str()
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            yield content
            return
        logger = Logger()
        settings = LLM_Settings()
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
                full_response += token
                yield token  # 立即返回当前 token

            if self.display_while_running:
                logger.log("")  # 打印换行
            

        except Exception as e:
            logger.log_error(e)
            raise  # 重新抛出异常

        logger.log_info("\nResult:")
        logger.log(Markdown(full_response))
        file_path = Path("selevaluator/data") / f"{self.course.course_name}.txt"  # 自动处理路径分隔符
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(full_response)
        return

