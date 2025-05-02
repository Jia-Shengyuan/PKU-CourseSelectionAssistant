import os
import time
from crawler.login import login
from crawler.search_courses import search_treehole
from scripts.search_from_config import get_courses

def main():
    # 首先登录并获取 driver
    driver = login()
    
    if driver:
        # course_list=get_courses()
        time.sleep(3)
        course_list = ["高等数学 (B) (二)", "普通物理 (Ⅰ)", "数学分析（II）", "高等代数 (II )", "程序设计实习"]
        
        # 初始的 HTML 内容
        html_content = "<html><body><h1>所有课程搜索结果</h1>"
        
        # 遍历课程并更新 HTML 内容
        for course in course_list:
            html_content = search_treehole(course, driver, html_content)
        
        # 完成 HTML 内容
        html_content += "</body></html>"

        # 保存文件到指定路径
        folder_path = "crawler"
        with open(os.path.join(folder_path, "all.html"), "w", encoding="utf-8") as f:
            f.write(html_content)

        print("已将所有课程的评论结果保存到 all.html 文件中。")
    else:
        print("登录失败，无法进行搜索。")

if __name__ == "__main__":
    main()
