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