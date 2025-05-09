import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio

def click_back_button(driver):
    try:
        close_xpath_1 = '//*[@id="eagleMapContainer"]/div[3]/div/div[2]/div[1]/div[1]/div/a/span'
        close_xpath_2 = '//*[@id="eagleMapContainer"]/div[4]/div/div[2]/div[1]/div[1]/div/a/span'
        
        try:
            back_button = driver.find_element(By.XPATH, close_xpath_1)
            back_button.click()
            return
        except Exception as e:
            pass

        try:
            back_button = driver.find_element(By.XPATH, close_xpath_2)
            back_button.click()
            return
        except Exception as e:
            pass

        print("没有找到关闭按钮，无法返回列表页面")

    except Exception as e:
        print(f"发生错误: {e}")

def getshort(course_name):
    ans=""
    for element in course_name:
        if element == '(' or element == '（':
            break
        else:
            ans += element
    return ans.strip()

def search_treehole(course_name, driver, html_content,max_len=5):
    course_name_short = getshort(course_name)
    select_name = course_name + " 测评"
    print("!"+course_name_short+"!")

    try:
        # 输入课程名并提交
        search_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[3]/div/div[1]/div/input'))
        )
        search_input.clear()
        search_input.send_keys(select_name)
        search_input.send_keys(Keys.RETURN)
        time.sleep(1)

        # 获取帖子列表
        posts = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="table_list"]/div/div'))
        )
        posts_count = min(len(posts), max_len)
        if posts_count > 0:
            print(f"找到{posts_count}个帖子：")
            
            for i in range(posts_count):
                try:
                    # 点击帖子
                    post = posts[i]
                    post_xpath = f'//*[@id="table_list"]/div/div[{i+1}]/div/div[1]/div'
                    post.click()

                    # 等待详细页面加载
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div'))
                    )

                    # 点赞按钮
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

                        # 获取所有评论
                        comments = driver.find_elements(By.XPATH, '//*[@id="detail-scroll detail-scroll2"]/div/div')
                        
                        for comment in comments:
                            comment_content = comment.text if comment else "无内容"
                            if course_name_short in comment_content:
                                print("find!")
                                if comment_content not in comments_collected:
                                    comments_collected.append(comment_content)
                                    html_content += f"<p>{comment_content}</p><hr>"

                    # 返回列表页面
                    click_back_button(driver)

                    # 等待列表页面重新加载
                    WebDriverWait(driver, 2).until(
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
