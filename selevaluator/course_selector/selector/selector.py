from ..agent.llm import LLM_API, LLM_Settings
from ..logger.logger import Logger
import json
import sys
import os
import glob
def load_json(file_path):
    """加载 JSON 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
# 2. 根据 course_name 搜索课程（支持模糊匹配）
def search_course(data, keyword):
    """按 course_name 搜索"""
    result = []
    for course in data:
        if keyword.lower() in course["course_name"].lower():  # 不区分大小写
            result.append(course)
    return result

student_config = load_json('config\config.example.json')
grade = student_config['user']['grade']
print(grade) 
class Selector:
    def __init__(self):
        logger = Logger()
        settings = LLM_Settings()
        llm = LLM_API(settings, logger)

        messages = [{"role": "system", "content": "你是一个课程筛选器" }]            
        try:
            with open("course_selector\plan.txt", "r", encoding='utf-8') as f:
                plan = f.read()
            messages.append({"role": "user", "content": f'''只从培养方案中提取出学生在{grade}的课程名称, \
                             按照必修和选修分类,输出格式:
required
课程名称1
课程名称2
...
selective
课程名称A
课程名称B
...
                             培养方案如下                          
                             ''' + plan})
            response = llm.chat(messages)
                
            self.full_response = ""
            logger.log("AI回复: ")

            for token in response:
                logger.log(token, end="")
                self.full_response += token

            logger.log("")
            messages.append({"role": "assistant", "content": self.full_response})
            
        except Exception as e:
            logger.log_error(f"发生错误: {str(e)}")