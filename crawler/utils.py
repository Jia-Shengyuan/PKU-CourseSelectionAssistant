import os

folder_path = "crawler"
data_folder_path = os.path.join(folder_path, "data")

def to_safe_filename(course_name):
    return "".join(c for c in course_name if c.isalnum() or c in (' ', '_')).rstrip()
