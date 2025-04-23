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

def get_courses_by_name(db: Session, name: str):
    # 罗马数字 → 阿拉伯数字 对照表
    from app.models.course import Course
    from sqlalchemy import or_
    roman_to_arabic = {
        "Ⅰ": "1", "Ⅱ": "2", "Ⅲ": "3", "Ⅳ": "4", "Ⅴ": "5",
        "Ⅵ": "6", "Ⅶ": "7", "Ⅷ": "8", "Ⅸ": "9", "Ⅹ": "10",
        "I": "1", "II": "2", "III": "3", "IV": "4", "V": "5",
        "VI": "6", "VII": "7", "VIII": "8", "IX": "9", "X": "10",
    }

    def normalize_name(name: str) -> str:
        # 替换罗马数字为阿拉伯数字
        for roman, arabic in roman_to_arabic.items():
            name = name.replace(roman, arabic)

        # 去除括号、特殊字符、空格
        name = re.sub(r"[（）()【】《》\[\]{}、·\s]", "", name)

        return name.lower()

    target = normalize_name(name)

    all_courses = db.query(Course).all()
    matched_courses = []

    for course in all_courses:
        if normalize_name(course.name) == target:
            matched_courses.append(course)

    return matched_courses