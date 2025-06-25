import pdfplumber
import re

def normalize_name(name: str) -> str:
    roman_to_arabic = {
        "Ⅲ": "3",  "Ⅱ": "2", "Ⅰ": "1",
        "III": "3", "II": "2", "I": "1"
    }
    kanji_to_arabic = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
        "六": "6", "七": "7", "八": "8", "九" : "9", "十": "10",
    }
    # 去除括号、特殊字符、空格
    name = re.sub(r"[（）()【】《》\[\]{}、·\s]", "", name)
    # 替换罗马数字为阿拉伯数字
    for roman, arabic in roman_to_arabic.items():
        name = name.replace(roman, arabic)
    for kanji, arabic in kanji_to_arabic.items():
        name = name.replace(kanji, arabic)
    return name.lower()

def read_pdf(pdf_path):
    results = ""
    useful_info = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.splitlines():
                if ("毕业要求" in line) or ("毕业总学分" in line):
                    useful_info = True
                if useful_info:
                    results = results + line + "\n"
    
    return results

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
            for line in text.split('\n'):
                parts = line.strip().split()
                course_name = ""
                if not parts[0].isdigit() or len(parts[0]) != 8:
                    continue
                course_id = parts[0]
                for part in parts[1:]:
                    if part in stop_keywords:
                        break
                    course_name = course_name + part
                alternative = '/' not in line
                if alternative:
                    alt_course = ""
                    for part in reversed(parts):
                        if part.isdigit():
                            break
                        alt_course = part + alt_course
                    for (_, course) in courses:
                        if course == alt_course:
                            courses.append((course_id, course_name))
                            break
                elif version1 in line or version2 in line or version3 in line:
                    courses.append((course_id, course_name))

    return courses