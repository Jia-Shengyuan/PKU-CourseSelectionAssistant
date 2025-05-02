import pandas as pd
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.course import Course
from app.db.base import Base
from app.schemas.course_schema import CourseCreate
from app.crud.course_crud import create_course
from scripts.load_config import load_semester

Base.metadata.create_all(bind=engine)

def read_excel(file_path: str):
    df = pd.read_excel(file_path, sheet_name=0)
    df.ffill()  # 将合并单元格内容填满
    return df

def clean_str(value):
    if pd.isna(value):
        return None
    return str(value)

def merge_course_rows(group):
    schedules = group['Schedule and Classroom'].dropna().astype(str).unique()
    schedule_str = '; '.join(schedules)

    return CourseCreate(
        course_id=str(group['ID'].iloc[0]),
        name=group['Name'].iloc[0],
        course_type=clean_str(group['Type'].iloc[0]),
        credit=float(group['Credit'].iloc[0] or 0),
        lecturer=clean_str(group['Lecturer'].iloc[0]),
        class_number=int(group['Class Number'].iloc[0]),
        school=clean_str(group['School'].iloc[0]),
        major=clean_str(group['Major'].iloc[0]),
        grade=clean_str(group['Grade'].iloc[0]),
        schedule_classroom=schedule_str or None,
        note=clean_str(group['Note'].iloc[0])
    )

def import_courses(file_path: str):
    df = read_excel(file_path)
    db: Session = SessionLocal()
    # 按课程名 + 教师分组
    grouped = df.groupby(['Name', 'Class Number'])

    count = 0
    for _, group in grouped:
        course = merge_course_rows(group)
        create_course(db, course)
        count += 1

    print(f"✅ 成功导入 {count} 门课程")

if __name__ == "__main__":
    semester = load_semester()
    import_courses("data/" + semester + ".xlsx")
