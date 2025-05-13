from sqlalchemy import Column, String, Integer, Float
from api.models.course import Course
from db.session.base import Base

class DbCourse(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # 新主键
    name = Column(String, index=True)
    course_id = Column(String, index=True)  # 原来的课程编号，不设为唯一
    class_id = Column(Float)
    teacher = Column(String, nullable=True)
    credit = Column(Float)
    time = Column(String, nullable=True)
    location=Column(String, nullable=True)
    note = Column(String, nullable=True)

class CourseCreate(Course):
    pass 

class CourseOut(Course):
    id : int

    class Config:
        from_attributes = True