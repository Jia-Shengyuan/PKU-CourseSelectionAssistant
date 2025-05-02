import json
import os

config_path = os.path.join("config", "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)



grade = config.get("user", {}).get("grade", str)
semester = config.get("user", {}).get("semester", str)
extra_courses = config.get("course", {}).get("extra_courses", [])
excluded_courses = config.get("course", {}).get("excluded_courses", [])

def load_grade():
    return grade
def load_semester():
    return semester
def load_extra_courses():
    return extra_courses
def load_excluded_courses():
    return excluded_courses