from app.db.session import SessionLocal
from app.crud.course_crud import get_courses_by_name

db = SessionLocal()
results = get_courses_by_name(db, "高等数学 (B) (二) ")
print(len(results))
for course in results:
    print(course.name, course.credit, course.lecturer, course.schedule_classroom)