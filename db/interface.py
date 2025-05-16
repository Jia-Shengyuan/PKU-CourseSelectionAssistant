import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from db.crud import get_courses_by_name
from db.utils import extract_courses_from_pdf

SessionLocal = None

def activate_database_(semester: str):
    global SessionLocal
    db_path = "./db/" + semester + ".db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

def get_course_info_(course_request: CourseSearchRequest):
    db = SessionLocal()
    name = course_request.name
    class_id = course_request.class_id
    teacher = course_request.teacher

    courses = get_courses_by_name(db, name)
    results = []
    for course in courses:
        if class_id != None and course.class_id != class_id:
            continue
        if teacher != None and teacher not in course.teacher:
            continue
        results.append(course)
    return results

def fetch_course_by_plan_(fetch_request: FetchCourseByPlanRequest):
    db = SessionLocal()
    semester = fetch_request.semester
    grade = fetch_request.grade
    plan_path = fetch_request.plan_path
    if semester[-1] == '1':
        semester = "上"
    elif semester[-1] =='2':
        semester = "下"
    else:
        return []
    course_name = extract_courses_from_pdf(plan_path, grade, semester)
    results = []
    for course in course_name:
        results = results + get_course_info_(CourseSearchRequest(name=course))
    return results

if __name__ == "__main__":
    activate_database_("2024-2025-2")
    print(fetch_course_by_plan_(FetchCourseByPlanRequest(semester="2024-2025-2", grade="大一", plan_path="./config/plan.pdf")))