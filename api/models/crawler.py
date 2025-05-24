from crawler.login import login
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
            self.driver = login()

    @staticmethod
    def get_instance():
        if TreeholeDriver._instance is None or TreeholeDriver._instance.driver is None:
            raise ValueError("Driver 未初始化，请先调用 login")
        return TreeholeDriver._instance.driver
