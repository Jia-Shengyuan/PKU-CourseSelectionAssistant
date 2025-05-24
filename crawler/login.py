import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_config():
    with open("config/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def is_logged_in(driver):
    try:
        driver.get("https://treehole.pku.edu.cn/")
        print("qwq")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span'))
        )
        return True
    except:
        return False

def login():
    config = get_config()
    chrome_user_data_dir = config["user"].get("chrome_user_data_dir")

    if not chrome_user_data_dir or not os.path.exists(chrome_user_data_dir):
        raise ValueError("请在 config.json 中设置有效的 Chrome 用户数据目录（chrome_user_data_dir）")

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
    options.add_argument("--remote-debugging-port=9222")  # 非必须，调试可用

    # 如果你希望避免多开冲突：
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 启动浏览器并尝试访问
    driver = webdriver.Chrome(options=options)
    if is_logged_in(driver):
        print("✅ 已复用浏览器登录状态，无需验证码。")
        return driver
    else:
        print("❌ 未检测到有效登录状态，请在打开的浏览器中手动登录...")

        # 等待用户手动登录，最多等待 90 秒
        for i in range(90):
            if is_logged_in(driver):
                print("✅ 手动登录成功！")
                return driver
            time.sleep(1)

        print("❌ 登录超时，请重试。")
        driver.quit()
        return None
