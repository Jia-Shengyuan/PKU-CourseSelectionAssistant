from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course_schema import CourseCreate

def get_course(db: Session, course_id: str):
    return db.query(Course).filter(Course.id == course_id).first()

def create_course(db: Session, course: CourseCreate):
    #print(course.model_dump())
    db_course = Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Course).offset(skip).limit(limit).all()