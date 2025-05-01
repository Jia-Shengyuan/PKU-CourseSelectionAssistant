import requests
import json
import time
import urllib.parse
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .search_courses import search_treehole
from bs4 import BeautifulSoup

term = 0  # 学期 0上1下

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
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    except FileNotFoundError:
        print("Cookies 文件未找到，无法加载 Cookies")

def login_with_cookies(driver, cookies_file='cookies.pkl'):
    """使用 Cookies 登录"""
    driver.get("https://treehole.pku.edu.cn/")
    load_cookies(driver, cookies_file)
    driver.refresh()  # 刷新页面来确保 Cookies 生效

def login():
    config = get_config()
    username = config.get("user", {}).get("student_id")
    password = config.get("user", {}).get("portal_password")
    grade = config.get("user", {}).get("grade")
    
    if "上" in grade:
        term = 0
    else:
        term = 1
    
    driver = webdriver.Chrome()
    session = requests.Session()

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
            cookies = driver.get_cookies()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            save_cookies(driver)  # 保存 Cookies
            return session, driver
        else:
            print("登录失败！")
            return None, None
    
    except Exception as e:
        print(f"发生错误: {e}")
        return None, None


def main():
    # 首先登录一次并保存 Cookies
    driver = webdriver.Chrome()
    session, driver = login()
    
    if session and driver:
        # 使用已经登录的 driver 进行后续搜索
        while True:
            course_name = input("请输入课程名称进行查询（输入 'exit' 退出）：")
            if course_name.lower() == 'exit':
                break
            search_treehole(course_name, driver)
        
        driver.quit()  # 结束浏览器会话
    else:
        print("登录失败，请检查用户名、密码或验证码问题。")
        
if __name__ == "__main__":
    main()
