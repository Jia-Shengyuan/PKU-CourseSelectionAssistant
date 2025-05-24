import os
import sys
import time
from login import login
from search_courses import search_treehole
from driver import TreeholeDriver

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from scripts.search_from_config import get_courses

folder_path="crawler"
data_folder_path = os.path.join(folder_path, "data")
os.makedirs(data_folder_path, exist_ok=True)

def main():
    # 首先登录并获取 driver
    driver = TreeholeDriver()
    driver.login()
    
    if driver:
        # course_list=get_courses()
        time.sleep(2)
        # course_list = ["高等数学 (B) (二)", "普通物理 (Ⅰ)", "数学分析（II）", "高等代数 (II )", "程序设计实习", "人工智能基础", "电磁学", "微电子与电路基础", "电子系统基础训练"]
        course_list = ["高等数学 (B) (二)",  "数学分析（II）"]
        
        # 遍历课程并更新 HTML 内容
        for course in course_list:        
            # 初始的 HTML 内容
            html_content = f"<html><body><h1>{course}</h1>"
            html_content = search_treehole(course, html_content, 5)  # 修正参数顺序
            html_content += "</body></html>"
            safe_course_name = "".join(c for c in course if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{safe_course_name}.html"
            with open(os.path.join(data_folder_path, filename), "w", encoding="utf-8") as f:
                f.write(html_content)
                
        print("已将所有课程的评论结果保存到 all.html 文件中。")
    else:
        print("登录失败，无法进行搜索。")

if __name__ == "__main__":
    main()

# taskkill /F /IM chrome.exe
# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

