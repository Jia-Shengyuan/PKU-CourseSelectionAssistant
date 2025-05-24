from crawler.login import new_login
from selenium.webdriver.chrome.webdriver import WebDriver
from typing import Optional

class TreeholeDriver:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TreeholeDriver, cls).__new__(cls)
            cls._instance.driver = None
        return cls._instance

    def login(self):
        if self.driver is None:
            # self.driver = login()
            self.driver = new_login()
            
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"❌ 关闭浏览器时出错: {e}")
            finally:
                self.driver = None
                TreeholeDriver._instance = None
        else:
            print("⚠️ 无需关闭，浏览器未初始化")

    @staticmethod
    def get_instance():
        if TreeholeDriver._instance is None or TreeholeDriver._instance.driver is None:
            raise ValueError("Driver 未初始化，请先调用 login")
        return TreeholeDriver._instance.driver
