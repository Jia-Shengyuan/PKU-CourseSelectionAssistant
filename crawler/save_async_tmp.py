

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

import os
import asyncio
from crawler.login_async import login_async
from crawler.search_courses import search_treehole_async_playwright
from scripts.search_from_config import get_courses

async def main_async():
    # 首先登录并获取 playwright 对象
    result = await login_async()
    
    if result:
        browser, context, page = result
        
        try:
            # course_list = get_courses()
            course_list = ["高等数学 (B) (二)", "普通物理 (Ⅰ)", "数学分析（II）", "高等代数 (II )", "程序设计实习"]
            
            # 初始的 HTML 内容
            html_content = "<html><body><h1>所有课程搜索结果</h1>"
            
            # 遍历课程并更新 HTML 内容
            for course in course_list:
                html_content = await search_treehole_async_playwright(course, page, html_content)
            
            # 完成 HTML 内容
            html_content += "</body></html>"

            # 保存文件到指定路径
            folder_path = "crawler"
            with open(os.path.join(folder_path, "all_async.html"), "w", encoding="utf-8") as f:
                f.write(html_content)

            print("已将所有课程的评论结果保存到 all_async.html 文件中。")
        
        finally:
            # 确保浏览器被关闭
            await browser.close()
    else:
        print("登录失败，无法进行搜索。")

if __name__ == "__main__":
    asyncio.run(main_async()) 
    
import json
import pickle
from playwright.async_api import async_playwright
import asyncio

def get_config():
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

async def save_cookies_async(context, cookies_file='cookies.pkl'):
    """保存 Cookies 到文件"""
    cookies = await context.cookies()
    with open(cookies_file, 'wb') as f:
        pickle.dump(cookies, f)

async def load_cookies_async(context, cookies_file='cookies.pkl'):
    """从文件加载 Cookies"""
    try:
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        await context.add_cookies(cookies)
        print("Cookies 加载成功")
    except FileNotFoundError:
        print("Cookies 文件未找到，无法加载 Cookies")

async def is_logged_in_async(page):
    """检查用户是否已登录"""
    try:
        await page.goto("https://treehole.pku.edu.cn/")
        await page.wait_for_selector('//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span')
        content = await page.content()
        if "北大树洞" in content:
            return True
        else:
            return False
    except Exception:
        return False

async def login_with_cookies_async(context, page, cookies_file='cookies.pkl'):
    """使用 Cookies 登录"""
    await page.goto("https://treehole.pku.edu.cn/")
    await load_cookies_async(context, cookies_file)
    await page.reload()  # 刷新页面来确保 Cookies 生效
    
    if await is_logged_in_async(page):
        print("Cookies 登录成功！")
        return True
    else:
        print("Cookies 无效，需要重新登录。")
        return False

async def login_async():
    """
    异步版本的登录函数
    返回: (browser, context, page) 元组，如果登录失败则返回 None
    """
    config = get_config()
    username = config.get("user", {}).get("student_id")
    password = config.get("user", {}).get("portal_password")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 先尝试加载 Cookies
        if not await login_with_cookies_async(context, page):
            # 如果没有有效的 Cookies，则进行手动登录
            try:
                await page.goto("https://treehole.pku.edu.cn/")
                
                # 等待用户名输入框出现并输入
                await page.wait_for_selector('input[name="userName"]')
                await page.fill('input[name="userName"]', username)
                
                # 输入密码
                await page.fill('input[name="password"]', password)
                
                # 点击登录按钮
                await page.click('#logon_button')

                print("请输入短信验证码...")

                # 等待登录成功
                await page.wait_for_selector('//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span')
                content = await page.content()
                
                if "北大树洞" in content:
                    print("登录成功！")
                    await save_cookies_async(context)  # 保存 Cookies
                    return browser, context, page
                else:
                    print("登录失败！")
                    await browser.close()
                    return None
            
            except Exception as e:
                print(f"发生错误: {e}")
                await browser.close()
                return None
        else:
            # 如果 Cookies 已经有效，直接返回
            return browser, context, page 