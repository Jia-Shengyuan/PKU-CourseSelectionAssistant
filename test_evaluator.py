import json
from course_evaluate.evaluator.evaluator import Evaluator
import sys

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
            return course_name, comments
    except FileNotFoundError:
        print(f"错误：文件 {json_file_path} 不存在")
        return None, None
    except json.JSONDecodeError:
        print(f"错误：文件 {json_file_path} 不是有效的JSON格式")
        return None, None

def main():
    # 指定JSON文件路径（根据实际情况修改）
    json_file = "course_evaluate\comments.json"  # 或者通过 sys.argv[1] 获取命令行参数
    
    # 从JSON提取数据
    course_name, comments = load_json_and_extract_fields(json_file)
    
    if course_name is None:
        return  # 提前终止
    
    print(f"已加载课程: {course_name}")
    print(f"评论内容: {comments[:50]}")  # 只打印前50字符

    # 创建Evaluator实例并传入数据
    test_evaluator = Evaluator(
        course_name=course_name,   
        comments=comments
    )
    


if __name__ == "__main__":
    main()
