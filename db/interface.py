import re
import pdfplumber
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from api.models.course import Course, CourseSearchRequest, FetchCourseByPlanRequest
from db.crud import get_courses_by_name, get_courses_by_id_
from db.utils import normalize_name, extract_courses_from_pdf, read_pdf
from db.dbmodel.dbcourse import DbCourse

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
    fuzzy_matching = course_request.fuzzy_matching
    accept_advanced_class = course_request.accept_advanced_class

    if accept_advanced_class == True and fuzzy_matching == False:
        raise ValueError("Database doesn't support automatically searching for advanced class when fuzzy matching is not allowed.")
        
    all_courses = db.query(DbCourse).all()
    results = []
    target = ""
    if fuzzy_matching:
        target = normalize_name(name)
    else:
        target = name
    
    for dbcourse in all_courses:
        course = Course(name=dbcourse.name,
                          course_id=dbcourse.course_id,
                          class_id=dbcourse.class_id,
                          teacher=dbcourse.teacher,
                          credit=dbcourse.credit,
                          time=dbcourse.time,
                          location=dbcourse.location,
                          note=dbcourse.note)
        course_name = ""
        if fuzzy_matching:
            course_name = normalize_name(course.name)
        else:
            course_name = course.name
        if course_name == target:
            if (class_id == None or class_id == course.class_id) and (teacher == None or teacher in course.teacher):
                results.append(course)
        if accept_advanced_class and "实验班" in course_name:
            course_name = re.sub(r"实验班", "", course_name) 
            if course_name == target:
                results.append(course)
    
    return results

def get_courses_by_id(id: str):
    db = SessionLocal()
    courses = get_courses_by_id_(db, id)
    return courses

def read_pdf_plan_(pdf_path: str):
    return read_pdf(pdf_path)

def fetch_course_by_plan_(fetch_request: FetchCourseByPlanRequest):
    semester = fetch_request.semester
    grade = fetch_request.grade
    plan_path = fetch_request.plan_path
    accept_advanced_class = fetch_request.accept_advanced_class
    if semester[-1] == '1':
        semester = "上"
    elif semester[-1] =='2':
        semester = "下"
    else:
        return []
    course_list = extract_courses_from_pdf(plan_path, grade, semester)
    results = []
    for (id, name) in course_list:
        results = results + get_courses_by_id(id)
        if accept_advanced_class:
            results = results + get_course_info_(CourseSearchRequest(name=name+"实验班", fuzzy_matching=True))
    return results

if __name__ == "__main__":
    activate_database_("2024-2025-2")
    #print(read_pdf_plan_("./config/plan.pdf"))
    #print(get_course_info_(CourseSearchRequest(name="网球", fuzzy_matching=True, accept_advanced_class=True)))
    #print(get_courses_by_id(id="132302"))
    print(fetch_course_by_plan_(FetchCourseByPlanRequest(semester="2024-2025-2", grade="大一", plan_path="./config/plan.pdf", experimental_class=True)))