import pdfplumber
import re

def extract_courses_from_pdf(pdf_path, target_grade, target_semester):
    courses = []

    version1 = target_grade + target_semester
    version2 = target_grade + '/' + target_semester
    version3 = target_grade + '/' + '上下'
    stop_keywords = {"全校必修", "专业必修", "任选", "限选", "专业选修", "专业核心课", "研究课程"}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.splitlines():
                # print(line)
                if target_grade not in line:
                    continue

                if version1 in line or version2 in line or version3 in line:
                    parts = line.strip().split()
                    course_name = ""
                    for part in parts[1:]:
                        if part in stop_keywords:
                            break
                        course_name = course_name + part
                    courses.append(course_name)

    return courses
