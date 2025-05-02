import json
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_config():
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def save_cookies(driver, cookies_file='cookies.pkl'):
    """保存 Cookies 到文件"""
    cookies = driver.get_cookies()
    with open(cookies_file, 'wb') as f:
        pickle.dump(cookies, f)

def load_cookies(driver, cookies_file='cookies.pkl'):
    """从文件加载 Cookies"""
    try:
        # 首先访问目标网站，以确保 cookies 能被成功加载
        driver.get("https://treehole.pku.edu.cn/")  # 确保访问目标域名

        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            # 如果 cookie 的域名不是我们要加载的域，修改它
            if 'domain' in cookie and cookie['domain'] != ".treehole.pku.edu.cn":
                cookie['domain'] = ".treehole.pku.edu.cn"  # 强制修正为正确的域名

            driver.add_cookie(cookie)

        print("Cookies 加载成功")
    except FileNotFoundError:
        print("Cookies 文件未找到，无法加载 Cookies")


def is_logged_in(driver):
    """检查用户是否已登录"""
    try:
        driver.get("https://treehole.pku.edu.cn/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span'))
        )
        if "北大树洞" in driver.page_source:
            return True
        else:
            return False
    except Exception:
        return False

def login_with_cookies(driver, cookies_file='cookies.pkl'):
    """使用 Cookies 登录"""
    driver.get("https://treehole.pku.edu.cn/")
    load_cookies(driver, cookies_file)
    driver.refresh()  # 刷新页面来确保 Cookies 生效
    
    if is_logged_in(driver):
        print("Cookies 登录成功！")
        return True
    else:
        print("Cookies 无效，需要重新登录。")
        return False

def login():
    config = get_config()
    username = config.get("user", {}).get("student_id")
    password = config.get("user", {}).get("portal_password")
    grade = config.get("user", {}).get("grade")
    
    driver = webdriver.Chrome()

    # 先尝试加载 Cookies
    if not login_with_cookies(driver):
        # 如果没有有效的 Cookies，则进行手动登录
        try:
            driver.get("https://treehole.pku.edu.cn/")
            
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "userName"))
            )
            username_input.send_keys(username)
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "logon_button"))
            )
            login_button.click()

            print("请输入短信验证码...")

            WebDriverWait(driver, 200).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span'))
            )

            if "北大树洞" in driver.page_source:
                print("登录成功！")
                save_cookies(driver)  # 保存 Cookies
                return driver
            else:
                print("登录失败！")
                return None
        
        except Exception as e:
            print(f"发生错误: {e}")
            return None
    else:
        # 如果 Cookies 已经有效，直接返回 driver
        return driver

### 有了cookies还要短信验证码？