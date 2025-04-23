import json
import os
import sys

from app.db.session import SessionLocal
from app.crud.course_crud import get_courses_by_name

# 1. 加载配置文件
config_path = os.path.join("config", "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
# 2. 读取 extra_course_list
grade = config.get("user", {}).get("grade", str)
extra_course_list = config.get("course", {}).get("extra_course_list", [])
excluded_course_list = config.get("course", {}).get("excluded_course_list", [])
# 3. 创建数据库会话
db = SessionLocal()

def get_courses():
    course_list = []
    # 4. 遍历查询课程
    for name in extra_course_list:

        if name in excluded_course_list:
            continue
        print(f"\n🔍 正在查找课程：{name}")
        results = get_courses_by_name(db, name)

        if not results:
            raise ValueError(" 没有找到该课程，请确认您在 config/config.json 中输入了正确的课程名称")
        else:
            print(f"✅ 课程查找成功：{name}")
            course_list = course_list + results
    return course_list

if __name__ == "__main__":
    try:
        results = get_courses()
    except ValueError as e:
        print(f"❌ 用户输入错误：{e}")
        sys.exit(1)

    for course in results:
        print(f"{course.name}-{course.lecturer}-{course.schedule_classroom}")