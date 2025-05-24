import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from api.models.crawler import TreeholeDriver  # 加上这行，使用 TreeholeDriver 单例

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
    for element in course_name:
        if element == '(' or element == '（':
            break
        ans += element
    return ans.strip()

def search_treehole(course_name: str, html_content: str, max_len: int = 5) -> str:
    driver = TreeholeDriver.get_instance()  # ✅ 单例获取 driver
    course_name_short = getshort(course_name)
    select_name = course_name + " 测评"
    print("!" + course_name_short + "!")

    try:
        search_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[3]/div/div[1]/div/input'))
        )
        search_input.clear()
        search_input.send_keys(select_name)
        search_input.send_keys(Keys.RETURN)
        time.sleep(1)

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
                    time.sleep(0.3)
                    new_height = driver.execute_script("return arguments[0].scrollHeight", comment_section)
                    if new_height == last_height:
                        break
                    last_height = new_height

                    comments = driver.find_elements(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div/div')
                    for comment in comments:
                        content = comment.text if comment else "无内容"
                        if course_name_short in content and content not in comments_collected:
                            print("find!")
                            comments_collected.append(content)
                            html_content += f"<p>{content}</p><hr>"

                click_back_button(driver)

                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="table_list"]/div/div'))
                )

            except Exception as e:
                print(f"抓取第{i+1}条帖子时发生错误: {e}")

    except Exception as e:
        print(f"发生错误: {e}")
    
    return html_content
