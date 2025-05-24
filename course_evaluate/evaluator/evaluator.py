from ..agent.llm import LLM_API, LLM_Settings
from ..logger.logger import Logger
import course_selector.selector.selector as selector
import json
import sys
import os
import glob
from pathlib import Path

class Summary:
    def __init__(self, course_name, comments, all_teacher):
        logger = Logger()
        settings = LLM_Settings()
        llm = LLM_API(settings, logger)
    

        messages = [{f"role": "system", "content": f"根据评价,先总体详细介绍一下课程, 再从按老师从优到劣推荐课程 老师有: {"或者".join(all_teacher)}, \
                     从给分,任务量,教学质量三个角度评价, 只保留老师的中文名" '''
格式类似 
电磁字课程总体评价
电磁学作为物理系的核心课程，内容涵盖静电场、静磁场、麦克斯韦方程组等，理论性较强但应用
泛。课程难度中等偏上，需要较好的数学基础(尤其是矢量分析和微积分)。大多数老师采用课堂讲授+作业+考试的模式，部
分老师会加入演示实验或数值模拟内容。
从往届学生反馈来看，电磁学的教学质量整体较好，但不同老师的授课风格和考核方式差异较大。
、下是按推荐程度排序的教师评价:
教师推荐(从优到劣)
沈波(教授) 给分 任务量 教学质量
何琼毅(教授)给分 任务量 教学质量'''}]            
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

class Evaluator:
    def __init__(self, course_name, comments, all_teacher):
        logger = Logger()
        settings = LLM_Settings()
        llm = LLM_API(settings, logger)

        messages = [{f"role": "system", "content": f"根据上述评价,给以下老师分别评分{"或者".join(all_teacher)}, \
                     从给分,教学质量角度,从0到100给老师的课程打分,分布尽量均匀,\
                     每个老师请以如下形式回答问题'Teacher: Point: Reason1: Reason2:' 其中Teacher只保留老师的中文名\
                     不同老师之间用 | 分割 "}]            
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

def evaluate_json_file(json_file, final_file):
    # 指定JSON文件路径（根据实际情况修改）
    
    # 从JSON提取数据
    course_name, comments = load_json_and_extract_fields(json_file)
    courses  = selector.load_json('data\processed_courses.json')
    search_results = selector.search_course(courses, course_name)
    print(f"{course_name} 找到 {len(search_results)} 个匹配结果：")
    all_teacher = []
    for course in search_results:
        all_teacher += course['teacher']
        print("--------------------")
        print(f"课程名称: {course['course_name']}")
        print(f"课程ID: {course['course_id']}")
        print(f"授课教师: {course['teacher']}")
        print(f"学分: {course['credit']}")
    if course_name is None:
        print("NO COURSE")
        return  # 提前终止
    
    #print(f"已加载课程: {course_name}")
    #print(f"评论内容: {comments[:50]}")  # 只打印前50字符

    # 创建Evaluator实例并传入数据
    '''E = Evaluator(
        course_name=course_name,  
        comments=comments,
        all_teacher = all_teacher,
    )'''
    S = Summary(
        course_name=course_name,  
        comments=comments,
        all_teacher = all_teacher,
    )
    #print(test_evaluator.full_response)
    '''all_evaluation = E.full_response.split("|")
    for comment in all_evaluation:
        add_course_review_to_json(
        comment,
        course_name,
        json_file= final_file,)'''
    file_path = Path("data") / "example.txt"  # 自动处理路径分隔符
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(S.full_response)

def html_to_json(html_file_name, json_file_name):
    import re
    with open(html_file_name, "r", encoding="utf-8") as file:
        html_first_line = file.readline()  # 读取第一行（如果有多行，可能需要调整）
        html_full = file.read() 
    pattern = r"<h1>(.*?)</h1>"              # 匹配 <h1>...</h1> 中间内容
    match = re.search(pattern, html_first_line)

    data = {
        "course_name": match.group(1),
        "comment": html_full,
    }
    with open(json_file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def evaluate_course(ls):
    clear_data_folder()
    final_file = r"course_evaluate\all_evaluation\evaluation.txt"
    for course_name in ls:
        from_file = r"crawler\data\\" + course_name + ".html"
        to_file = r"course_evaluate\raw_comments\\" + course_name + ".json" 
        html_to_json(from_file, to_file)
        evaluate_json_file(to_file, final_file)
        #final_file = r"course_evaluate\data\\" + course_name + ".json" 分开的输出
        

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
        if line.startswith("Teacher:"):
            data["Teacher"] = line.split(":")[1].strip()
        elif line.startswith("Point:"):
            data["Point"] = int(line.split("Point:")[1].strip())
        elif line.startswith("Reason1:"):
            data["Reason1"] = line.split("Reason1:")[1].strip()
        elif line.startswith("Reason2:"):
            data["Reason2"] = line.split("Reason2:")[1].strip()
    # 2. 检查是否所有必要的字段都存在
    required_fields = ["Teacher", "Point", "Reason1", "Reason2"]
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
    courses  = selector.load_json('data\processed_courses.json')
    search_results = selector.search_course(courses, course_name)
    print(f"{course_name} 找到 {len(search_results)} 个匹配结果：")
    data['credit'] = search_results[0]['credit']
    data['time'] = search_results[0]['time']
    data['location'] = search_results[0]['location']
    existing_data[course_name].append(data)  # 加入新评价
    # 5. 写回 JSON 文件
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
    print(f"✅ 评价已添加到 {course_name} 下，存储至 {json_file}")

def clear_data_folder():
    json_files = glob.glob(r"course_evaluate\all_evaluation\*.txt")
    for file in json_files:
        os.remove(file)
        print(f"已删除: {file}")