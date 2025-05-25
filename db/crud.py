from sqlalchemy.orm import Session
from api.models.course import Course
from db.dbmodel.dbcourse import DbCourse, CourseCreate
from db.utils import normalize_name
import re

def get_course(db: Session, course_id: str):
    return db.query(DbCourse).filter(DbCourse.id == course_id).first()

def create_course(db: Session, course: CourseCreate):
    #print(course.model_dump())
    db_course = DbCourse(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_courses_by_name(db: Session, name: str, fuzzy_matching: bool):
    # 罗马数字 → 阿拉伯数字 对照表

    target = ""
    if fuzzy_matching:
        target = normalize_name(name)
    else:
        target = name

    all_courses = db.query(DbCourse).all()
    matched_courses = []

    for dbcourse in all_courses:
        course_name = ""
        if fuzzy_matching:
            course_name = normalize_name(dbcourse.name)
        else:
            course_name = dbcourse.name
        if course_name == target:
            course=Course(name=dbcourse.name,
                          course_id=dbcourse.course_id,
                          class_id=dbcourse.class_id,
                          teacher=dbcourse.teacher,
                          credit=dbcourse.credit,
                          time=dbcourse.time,
                          location=dbcourse.location,
                          note=dbcourse.note)
            matched_courses.append(course)

    return matched_courses

def get_courses_by_id_(db: Session, id: str):
    all_courses = db.query(DbCourse).all()
    matched_courses = []

    for dbcourse in all_courses:
        if dbcourse.course_id.lstrip('0') == id.lstrip('0'):
            course=Course(name=dbcourse.name,
                          course_id=dbcourse.course_id,
                          class_id=dbcourse.class_id,
                          teacher=dbcourse.teacher,
                          credit=dbcourse.credit,
                          time=dbcourse.time,
                          location=dbcourse.location,
                          note=dbcourse.note)
            matched_courses.append(course)

    return matched_courses