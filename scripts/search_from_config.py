import json
import os
import sys
from scripts.search_in_pdf import extract_courses_from_pdf
from scripts.load_config import load_grade, load_extra_courses, load_excluded_courses
from scripts.search_file import search_by_suffix
from app.db.session import SessionLocal
from app.crud.course_crud import get_courses_by_name, normalize_name

# 1. 加载配置文件
config_path = os.path.join("config", "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
# 2. 读取 extra_course_list
grade = load_grade()
semester = grade[2:]
grade = grade[:2]
extra_courses = load_extra_courses()
excluded_course_list = load_excluded_courses()
# 3. 创建数据库会话
db = SessionLocal()

def get_pdf():
    files = search_by_suffix("./config", ".pdf")
    if not files:
        raise ValueError("请确认您将培养方案保存在 ./config 目录下")
    elif len(files)>1:
        raise ValueError("请确认在 ./config 目录下只保存了培养方案一个pdf文件")
    else:
        return "./config/" + files[0]


def get_courses():
    pdf_path = get_pdf()
    plan_courses = extract_courses_from_pdf(pdf_path, grade, semester)
    target_courses = extra_courses + plan_courses
    course_list = []
    normalized_courses = list(map(normalize_name, target_courses))
    # 4. 遍历查询课程
    for name in normalized_courses:
        if name in excluded_course_list:
            continue
        print(f"\n🔍 正在查找课程：{name}")
        results = get_courses_by_name(db, name)

        if not results:
            raise ValueError(" 没有找到该课程，请确认您在 config/config.json 中输入了正确的课程名称")
        else:
            print(f"✅ 课程查找成功：{name}")
            course_list.append((name, results))

    return course_list

if __name__ == "__main__":
    try:
        results = get_courses()
    except ValueError as e:
        print(f"❌ 用户输入错误：{e}")
        sys.exit(1)

    for (name, infos) in results:
        print(f"{name}:")
        for course in infos:
            print(f"{course.lecturer}-{course.schedule_classroom}-{course.note}")