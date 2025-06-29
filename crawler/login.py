import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_config():
    with open("config/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def is_logged_in(driver):
    try:
        driver.get("about:blank")
        time.sleep(0.5)
        driver.get("https://treehole.pku.edu.cn/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="eagleMapContainer"]/div[1]/div[2]/div/p/span'))
        )
        return True
    except:
        return False

def login():
    config = get_config()
    chrome_user_data_dir = config["crawler"].get("chrome_user_data_dir")

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

def new_login():
    """
    使用webdriver_manager自动管理ChromeDriver版本的登录函数
    功能与login()完全相同，只是自动处理ChromeDriver版本
    """
    config = get_config()
    chrome_user_data_dir = config["crawler"].get("chrome_user_data_dir")

    if not chrome_user_data_dir:
        raise ValueError("请在 config.json 中设置 Chrome 用户数据目录（chrome_user_data_dir）")

    # 将相对路径转换为绝对路径
    if not os.path.isabs(chrome_user_data_dir):
        # 获取项目根目录的绝对路径
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        chrome_user_data_dir = os.path.abspath(os.path.join(project_root, chrome_user_data_dir))

    # 确保目录存在
    os.makedirs(chrome_user_data_dir, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
    options.add_argument("--remote-debugging-port=9222")  # 非必须，调试可用

    # 如果你希望避免多开冲突：
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 使用webdriver_manager自动管理ChromeDriver版本
    # try:
        # 启动浏览器并尝试访问
        # service = Service(ChromeDriverManager(cache_valid_range=7).install()) 
    # except:
        # 如果失败，可能是因为Chrome更新后webdriver_manager没有及时更新
        # 因此我们不使用缓存重新尝试
        # print("尝试不使用缓存启动ChromeDriver...")
    service = Service(ChromeDriverManager().install())

    print("正在启动Chrome浏览器，请稍候...")

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ Chrome浏览器启动失败！")
        if "cannot find Chrome binary" in str(e):
            print("错误原因：未找到Chrome浏览器。")
            print("解决方案：")
            print("1. 请下载并安装Chrome浏览器：https://www.google.com/chrome/")
            print("2. 确保Chrome已正确安装在默认路径")
            print("3. 如果Chrome安装在非默认路径，请将其添加到系统PATH环境变量")
        else:
            print(f"错误详情：{e}")
        raise e
    
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
