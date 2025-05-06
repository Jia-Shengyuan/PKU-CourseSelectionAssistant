from pydantic import BaseModel
from typing import Optional

class CourseSearchRequest(BaseModel):
    name: str
    class_id: Optional[int] = None
    teacher: Optional[str] = None

class Course(BaseModel):
    name: str
    class_id: int
    teacher: str
    credit: int
    time: str
    location: str
    course_id: str
    note: Optional[str] = None
    course_type: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
