from pydantic import BaseModel
from typing import Optional

class CourseSearchRequest(BaseModel):
    name: str
    class_id: Optional[float] = None
    teacher: Optional[str] = None
<<<<<<< HEAD
    experimental_class: Optional[bool] = False
=======
    accept_advanced_class: Optional[bool] = False
>>>>>>> f128e3ecb2f345f02467819f5a44c139275d66d6

class FetchCourseByPlanRequest(BaseModel):
    semester: str
    grade: str
    plan_path: str
    experimental_class: Optional[bool] = False


class Course(BaseModel):
    name: str
    course_id: str
    class_id: float
    teacher: Optional[str] = None
    credit: float
    time: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None