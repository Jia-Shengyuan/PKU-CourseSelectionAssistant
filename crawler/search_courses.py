import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from crawler.driver import TreeholeDriver
from crawler.utils import data_folder_path, to_safe_filename

def click_back_button(driver):
    try:
        close_xpath_1 = '//*[@id="eagleMapContainer"]/div[3]/div/div[2]/div[1]/div[1]/div/a/span'
        close_xpath_2 = '//*[@id="eagleMapContainer"]/div[4]/div/div[2]/div[1]/div[1]/div/a/span'

        for xpath in [close_xpath_1, close_xpath_2]:
            try:
                driver.find_element(By.XPATH, xpath).click()
                return
            except:
                continue
        print("没有找到关闭按钮，无法返回列表页面")
    except Exception as e:
        print(f"发生错误: {e}")

def getshort(course_name):
    ans = ""
    flag=0
    for element in course_name:
        if element == '(' or element == '（':
            flag=1
        if flag==0:
            ans += element
        if element == ')' or element == '）':
            flag=0
    return ans.strip()

def search_treehole(course_name: str, teacher: str,html_content: str, max_len: int = 5, sleep_after_search: float = 1, sleep_between_scroll: float = 0.3, save_results: bool = True, acceppt_saved_results: bool = True) -> str:
    
    # If accpect saved results, and the corresponding file exists, then just return without searching again.
    if acceppt_saved_results:
        filename = f"{to_safe_filename(course_name)}.html"
        if os.path.exists(os.path.join(data_folder_path, filename)):
            with open(os.path.join(data_folder_path, filename), "r", encoding="utf-8") as f:
                html_content = f.read()
            return html_content

    driver = TreeholeDriver.get_instance()
    course_name_short = getshort(course_name)
    query_name = f"{course_name_short} {teacher}"
    select_name = query_name + " 测评"
    print("!" + query_name + "!")

    try:
        search_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[3]/div/div[1]/div/input'))
        )
        search_input.clear()
        search_input.send_keys(select_name)
        search_input.send_keys(Keys.RETURN)
        time.sleep(sleep_after_search)

        posts = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="table_list"]/div/div'))
        )
        posts_count = min(len(posts), max_len)
        print(f"找到{posts_count}个帖子：")

        for i in range(posts_count):
            try:
                post_xpath = f'//*[@id="table_list"]/div/div[{i+1}]/div/div[1]/div'
                driver.find_element(By.XPATH, post_xpath).click()

                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div'))
                )

                dz_only = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div/div[3]/div[1]/div/span[1]/span'))
                )
                dz_only.click()

                comment_section = driver.find_element(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]')
                last_height = driver.execute_script("return arguments[0].scrollHeight", comment_section)
                comments_collected = []

                while True:
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comment_section)
                    time.sleep(sleep_between_scroll)
                    new_height = driver.execute_script("return arguments[0].scrollHeight", comment_section)
                    last_height = new_height
                    comments = driver.find_elements(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div/div')
                    for comment in comments:
                        content = comment.text if comment else "无内容"
                        if course_name_short in content and content not in comments_collected:
                            print("find!")
                            comments_collected.append(content)
                            html_content += f"<p>{content}</p><hr>"
                    if new_height == last_height:
                        break

                click_back_button(driver)

                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="table_list"]/div/div'))
                )

            except Exception as e:
                print(f"抓取第{i+1}条帖子时发生错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")

    if save_results:
        filename = f"{to_safe_filename(course_name)}.html"
        with open(os.path.join(data_folder_path, filename), "w", encoding="utf-8") as f:
            f.write(html_content)
    
    return html_content
