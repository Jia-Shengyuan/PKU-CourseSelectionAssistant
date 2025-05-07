import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright
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

def search_treehole(course_name, driver, html_content):
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

        # 获取帖子列表
        posts = WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="table_list"]/div/div'))
        )
        posts_count = min(len(posts), 5)
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


'''
    我询问了AI关于如何基于你的代码将搜索的过程异步化，他告诉我原来是selenium是同步的，也就是等待他执行的时候会阻塞主进程
    然后我让他新写一份，得到了这样的函数。后面我又让AI参照着你的写的login_async和main_async。
    这三段代码我都没有运行过，不知道是对是错，大概率是有错的。但有错也大概率不是大错？总之你可以参照一下。

    如果要运行，需要安装相关库：先pip install playwright，然后playwright install

    AI：让我解释一下这两个命令的区别：
    pip install playwright：
    这是安装 Playwright 的 Python 包
    只安装 Python 的 API 接口和必要的 Python 依赖
    相当于安装了一个"控制面板"，让你可以用 Python 代码来控制浏览器
    playwright install：
    这是安装 Playwright 需要的浏览器驱动
    会下载 Chromium、Firefox 和 WebKit 等浏览器的特定版本
    这些浏览器是经过 Playwright 团队特别定制的版本，包含了自动化所需的所有功能
    相当于安装"实际的浏览器"，这些浏览器会被 Playwright 控制
'''
async def search_treehole_async_playwright(course_name, page, html_content):
    """
    使用playwright的异步版本搜索树洞
    :param course_name: 课程名称
    :param page: 已经登录的playwright页面对象
    :param html_content: 累积的HTML内容
    :return: 更新后的HTML内容
    """
    course_name_short = getshort(course_name)
    select_name = course_name + " 测评"
    print("!"+course_name_short+"!")

    try:
        # 访问树洞
        await page.goto('https://treehole.pku.edu.cn/')
        
        # 等待搜索框出现并输入
        search_input = await page.wait_for_selector('//*[@id="eagleMapContainer"]/div[1]/div[3]/div/div[1]/div/input')
        await search_input.fill(select_name)
        await search_input.press('Enter')

        # 等待帖子列表加载
        posts = await page.query_selector_all('//*[@id="table_list"]/div/div')
        posts_count = min(len(posts), 5)

        if posts_count > 0:
            print(f"找到{posts_count}个帖子：")
            
            for i in range(posts_count):
                try:
                    # 点击帖子
                    post = posts[i]
                    await post.click()

                    # 等待详细页面加载
                    await page.wait_for_selector('//*[@id="detail-scroll detail-scroll2"]/div')

                    # 点击点赞按钮
                    dz_button = await page.wait_for_selector('//*[@id="detail-scroll detail-scroll2"]/div/div[3]/div[1]/div/span[1]/span')
                    await dz_button.click()

                    # 获取评论区域
                    comment_section = await page.query_selector('//*[@id="detail-scroll detail-scroll2"]')
                    comments_collected = []

                    while True:
                        # 滚动到底部
                        await page.evaluate('(element) => { element.scrollTop = element.scrollHeight }', comment_section)
                        await asyncio.sleep(0.3)

                        # 获取新的高度
                        new_height = await page.evaluate('(element) => element.scrollHeight', comment_section)
                        last_height = await page.evaluate('(element) => element.scrollHeight', comment_section)
                        
                        if new_height == last_height:
                            break

                        # 获取所有评论
                        comments = await page.query_selector_all('//*[@id="detail-scroll detail-scroll2"]/div/div')
                        
                        for comment in comments:
                            comment_content = await comment.text_content()
                            if comment_content and course_name_short in comment_content:
                                print("find!")
                                if comment_content not in comments_collected:
                                    comments_collected.append(comment_content)
                                    html_content += f"<p>{comment_content}</p><hr>"

                    # 返回列表页面
                    back_button = await page.query_selector('//*[@id="eagleMapContainer"]/div[3]/div/div[2]/div[1]/div[1]/div/a/span')
                    if not back_button:
                        back_button = await page.query_selector('//*[@id="eagleMapContainer"]/div[4]/div/div[2]/div[1]/div[1]/div/a/span')
                    if back_button:
                        await back_button.click()
                    else:
                        print("没有找到关闭按钮，无法返回列表页面")

                    # 等待列表页面重新加载
                    await page.wait_for_selector('//*[@id="table_list"]/div/div')

                except Exception as e:
                    print(f"抓取第{i+1}条帖子时发生错误: {e}")
                    content = "无内容"

        else:
            print(f"没有找到与'{course_name}'相关的帖子。")

    except Exception as e:
        print(f"发生错误: {e}")
    
    return html_content