from ..agent.llm import LLM_API, LLM_Settings
from ..logger.logger import Logger
import json
import sys
import os
def load_json_and_extract_fields(json_file_path):
    """
    加载JSON文件并提取course_name和comments字段
    :param json_file_path: JSON文件路径
    :return: (course_name, comments) 元组
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 提取字段（假设数据是字典格式）
            course_name = data.get("course_name", "")
            comments = data.get("comments", "")
            teacher = data.get("teacher", "")
            return course_name, comments
    except FileNotFoundError:
        print(f"错误：文件 {json_file_path} 不存在")
        return None, None
    except json.JSONDecodeError:
        print(f"错误：文件 {json_file_path} 不是有效的JSON格式")
        return None, None

def add_course_review_to_json(
    input_str,
    course_name,
    json_file="course_reviews.json",
):
    """
    将课程评价（Point, Reason1, Reason2）加入到 JSON 文件的 `course_name` 下。
    :param input_str: 输入的评价字符串（含 Point/Reason1/Reason2）
    :param course_name: 课程名称（如 "Algorithm"）
    :param json_file: JSON 文件路径（默认 course_reviews.json）
    """
    
    # 1. 解析输入字符串
    lines = input_str.strip().split("\n")
    # 提取 Point, Reason1, Reason2
    data = {}
    for line in lines:
        line = line.strip()
        if line.startswith("Point:"):
            data["Point"] = int(line.split(":")[1].strip())
        elif line.startswith("Reason1:"):
            data["Reason1"] = line.split("Reason1:")[1].strip()
        elif line.startswith("Reason2:"):
            data["Reason2"] = line.split("Reason2:")[1].strip()
    # 2. 检查是否所有必要的字段都存在
    required_fields = ["Point", "Reason1", "Reason2"]
    if not all(field in data for field in required_fields):
        raise ValueError("输入字符串缺少 Point / Reason1 / Reason2 其中一项")
    # 3. 读取现有的 JSON 数据（如果文件存在）
    existing_data = {}
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    # 4. 更新数据（如果 `course_name` 不存在，则创建）
    if course_name not in existing_data:
        existing_data[course_name] = []
    
    existing_data[course_name].append(data)  # 加入新评价
    # 5. 写回 JSON 文件
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
    print(f"✅ 评价已添加到 {course_name} 下，存储至 {json_file}")

class Evaluator:
    def __init__(self, course_name, comments):
        logger = Logger()
        settings = LLM_Settings()
        llm = LLM_API(settings, logger)

        messages = [{"role": "system", "content": "请评论给课程打分,评价为上过课的学长所写,根据上述评价,从给分,教学质量角度,从0到10给课程打分,请以如下形式回答问题'Point: Reason1: Reason2' "}]            
        try:

            messages.append({"role": "user", "content": "课程名称:" + course_name + " 评价:" + comments})
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

def evaluate_jason_file(json_file = "course_evaluate\comments.json"):
    # 指定JSON文件路径（根据实际情况修改）
    
    # 从JSON提取数据
    course_name, comments = load_json_and_extract_fields(json_file)
    
    if course_name is None:
        return  # 提前终止
    
    #print(f"已加载课程: {course_name}")
    #print(f"评论内容: {comments[:50]}")  # 只打印前50字符

    # 创建Evaluator实例并传入数据
    test_evaluator = Evaluator(
        course_name=course_name,   
        comments=comments
    )
    print(test_evaluator.full_response)
    add_course_review_to_json(
    test_evaluator.full_response,
    course_name,
    json_file="course_reviews.json",)




