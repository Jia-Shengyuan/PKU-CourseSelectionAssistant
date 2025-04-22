from sqlalchemy import Column, String, Integer, Float
from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # 新主键
    course_id = Column(String, index=True)  # 原来的课程编号，不设为唯一
    name = Column(String, index=True)
    course_type = Column(String)
    credit = Column(Integer)
    lecturer = Column(String, nullable=True)
    class_number = Column(Integer)
    school = Column(String)
    major = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    schedule_classroom = Column(String, nullable=True)
    note = Column(String, nullable=True)