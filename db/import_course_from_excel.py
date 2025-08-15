import pandas as pd
from sqlalchemy.orm import Session
from db.session.session import SessionLocal, engine
from db.dbmodel.dbcourse import DbCourse, CourseCreate
from db.session.base import Base
from db.crud import create_course

'''
Run this code to generate .db database from processed excel timetables.
Command: python -m db.import_course_from_excel (Run in the root directory)
'''

Base.metadata.create_all(bind=engine)

def read_excel(file_path: str):
    df = pd.read_excel(file_path, sheet_name=0)
    df.replace("", pd.NA, inplace=True)
    df['course_name'] = df['course_name'].ffill()
    df['course_id'] = df['course_id'].ffill()
    df['class_id'] = df['class_id'].ffill()
    return df

def clean_str(value):
    if pd.isna(value):
        return None
    return str(value)

def merge_course_rows(group):
    times = group['time'].dropna().astype(str).unique()
    times = '; '.join(times)
    return CourseCreate(
        name=group['course_name'].iloc[0],
        course_id=str(group['course_id'].iloc[0]),
        teacher=clean_str(group['teacher'].iloc[0]),
        credit=float(group['credit'].iloc[0]),
        class_id=float(group['class_id'].iloc[0]),
        time=times or None,
        location=clean_str(group['location'].iloc[0]),
        note=clean_str(group['note'].iloc[0])
    )

def import_courses(file_path: str):
    df = read_excel(file_path)
    db: Session = SessionLocal()
    # 按课程名 + 教师分组
    grouped = df.groupby(['course_name', 'class_id'])

    count = 0
    for _, group in grouped:
        course = merge_course_rows(group)
        create_course(db, course)
        count += 1

    print(f"✅ 成功导入 {count} 门课程")

if __name__ == "__main__":
    import_courses("data/2025-2026-1_processed.xlsx")
