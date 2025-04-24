from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course_schema import CourseCreate
import re

def get_course(db: Session, course_id: str):
    return db.query(Course).filter(Course.id == course_id).first()

def create_course(db: Session, course: CourseCreate):
    #print(course.model_dump())
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def normalize_name(name: str) -> str:
    from app.models.course import Course
    from sqlalchemy import or_
    roman_to_arabic = {
        "Ⅲ": "3",  "Ⅱ": "2", "Ⅰ": "1",
        "III": "3", "II": "2", "I": "1"
    }
    kanji_to_arabic = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
        "六": "6", "七": "7", "八": "8", "九" : "9", "十": "10",
    }
    # 去除括号、特殊字符、空格
    name = re.sub(r"[（）()【】《》\[\]{}、·\s]", "", name)
    # 替换罗马数字为阿拉伯数字
    for roman, arabic in roman_to_arabic.items():
        name = name.replace(roman, arabic)
    for kanji, arabic in kanji_to_arabic.items():
        name = name.replace(kanji, arabic)
    return name.lower()

def get_courses_by_name(db: Session, name: str):
    # 罗马数字 → 阿拉伯数字 对照表

    target = normalize_name(name)

    all_courses = db.query(Course).all()
    matched_courses = []

    for course in all_courses:
        if normalize_name(course.name) == target:
            matched_courses.append(course)

    return matched_courses