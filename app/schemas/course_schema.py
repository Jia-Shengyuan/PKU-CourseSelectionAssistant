from pydantic import BaseModel
from typing import Optional

# 公共基类（用于Create和Out共用字段）
class CourseBase(BaseModel):
    course_id: str                  # 原来的 id，课程编号，不再唯一
    name: str
    course_type: str
    credit: float
    lecturer: Optional[str] = None
    class_number: float                  # 改为 str，避免 float 问题
    school: str
    major: Optional[str] = None
    grade: Optional[str] = None
    schedule_classroom: Optional[str] = None
    note: Optional[str] = None

# 创建时使用的模型，不含数据库主键id
class CourseCreate(CourseBase):
    pass

# 输出时包含数据库主键id（自动生成的）
class CourseOut(CourseBase):
    id: int # 自动生成的主键ID

    class Config:
        from_attributes = True