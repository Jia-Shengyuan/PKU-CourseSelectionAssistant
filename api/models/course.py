from pydantic import BaseModel
from typing import Optional

class CourseSearchRequest(BaseModel):
    name: str
    class_id: Optional[int] = None
    teacher: Optional[str] = None

class FetchCourseByPlanRequest(BaseModel):
    semester: str
    grade: str
    plan_path: str


class Course(BaseModel):
    name: str
    course_id: str
    class_id: float
    teacher: Optional[str] = None
    credit: float
    time: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None