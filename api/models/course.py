from pydantic import BaseModel
from typing import Optional

class CourseSearchRequest(BaseModel):
    name: str
    teacher: Optional[str] = None
    class_id: Optional[float] = None
    fuzzy_matching: Optional[bool] = True
    accept_advanced_class: Optional[bool] = False

class FetchCourseByPlanRequest(BaseModel):
    grade: str
    semester: str
    plan_path: str
    accept_advanced_class: Optional[bool] = False


class Course(BaseModel):
    name: str
    note: Optional[str] = None
    time: Optional[str] = None
    credit: Optional[float] = 0
    teacher: Optional[str] = None
    class_id: float
    location: Optional[str] = None
    course_id: str