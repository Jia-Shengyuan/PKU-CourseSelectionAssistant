from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.search_from_config import get_courses

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=chrome_options)

def click_back_button(driver):
    try:
        close_xpath_1 = '//*[@id="eagleMapContainer"]/div[3]/div/div[2]/div[1]/div[1]/div/a/span'
        close_xpath_2 = '//*[@id="eagleMapContainer"]/div[4]/div/div[2]/div[1]/div[1]/div/a/span'
        
        try:
            back_button = driver.find_element(By.XPATH, close_xpath_1)
            back_button.click()
            time.sleep(2)
            return
        except Exception as e:
            pass

        try:
            back_button = driver.find_element(By.XPATH, close_xpath_2)
            back_button.click()
            time.sleep(2)
            return
        except Exception as e:
            pass

        print("没有找到关闭按钮，无法返回列表页面")

    except Exception as e:
        print(f"发生错误: {e}")


def search_treehole(course_name, driver, html_content):
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[3]/div/div[1]/div/input'))
        )
        search_input.clear()
        search_input.send_keys(course_name)
        search_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="table_list"]/div/div[1]/div/div[1]/div/div[1]/span[3]/span'))
        )

        posts = driver.find_elements(By.XPATH, '//*[@id="table_list"]/div/div')

        posts_count = min(len(posts), 3)

        if posts_count > 0:
            print(f"找到{posts_count}个帖子：")
            
            for i in range(posts_count):
                try:
                    post = posts[i]
                    post_xpath = f'//*[@id="table_list"]/div/div[{i+1}]/div/div[1]/div'
                    post.click()

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div'))
                    )

                    content = post.find_element(By.XPATH, post_xpath).text if post.find_element(By.XPATH, post_xpath) else "无内容"
                    print(f"帖子内容: {content}")

                    comment_section = driver.find_element(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]')

                    last_height = driver.execute_script("return arguments[0].scrollHeight", comment_section)
                    comments_collected = []

                    while True:
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comment_section)
                        time.sleep(3)

                        new_height = driver.execute_script("return arguments[0].scrollHeight", comment_section)
                        if new_height == last_height:
                            break
                        last_height = new_height

                        comments = driver.find_elements(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div/div')
                        
                        for comment in comments:
                            comment_content = comment.text if comment else "无内容"
                            if comment_content not in comments_collected:
                                print(f"评论内容: {comment_content}")
                                comments_collected.append(comment_content)
                                html_content += f"<p>{comment_content}</p><hr>"

                    click_back_button(driver)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="table_list"]/div/div'))
                    )

                except Exception as e:
                    print(f"抓取第{i+1}条帖子时发生错误: {e}")
                    content = "无内容"

        else:
            print(f"没有找到与'{course_name}'相关的帖子。")
    except Exception as e:
        print(f"发生错误: {e}")
    
    return html_content


course_list=["高等数学 (B) (二)","普通物理 (Ⅰ)","数学分析（II）","高等代数 (II )","程序设计实习","人工智能基础","电磁学","微电子与电路基础","电子系统基础训练"]

html_content = "<html><body><h1>所有课程搜索结果</h1>"

for course in course_list:
    course_name = course + " 测评"
    html_content = search_treehole(course_name, driver, html_content)

html_content += "</body></html>"

with open("all_courses_search_results.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("已将所有课程的评论结果保存到 all_courses_search_results.html 文件中。")
