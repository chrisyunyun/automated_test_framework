"""
示例页面类 - 登录页面和首页
实现具体的页面对象，继承自 BasePage
每个页面对应一个类，包含该页面的元素定位器和操作方法
"""
# 从 playwright 同步 API 导入 Page 对象类型注解
from playwright.sync_api import Page
# 从基类模块导入 BasePage，所有页面类都继承它
from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    登录页面对象类
    封装登录页面的所有元素和操作
    继承自 BasePage，自动拥有所有通用操作方法
    """
    
    # ============================================
    # 元素定位器（类常量）
    # 集中管理页面元素的选择器，便于维护
    # ============================================
    
    # 用户名输入框的 CSS 选择器
    USERNAME_INPUT = "#username"
    
    # 密码输入框的 CSS 选择器
    PASSWORD_INPUT = "#password"
    
    # 登录按钮的 CSS 选择器
    LOGIN_BUTTON = "#login-btn"
    
    # 错误消息元素的 CSS 选择器
    ERROR_MESSAGE = ".error-message"
    
    # 成功消息元素的 CSS 选择器
    SUCCESS_MESSAGE = ".success-message"
    
    def __init__(self, page: Page):
        """
        初始化登录页面对象
        :param page: Playwright 的 Page 对象
        """
        # 调用父类 BasePage 的构造函数
        # 初始化 self.page, self.base_url, self.timeout
        super().__init__(page)
    
    def navigate(self):
        """
        导航到登录页面
        :return: 返回 self，支持链式调用
        """
        # 调用父类的 goto 方法，导航到 "login" 路径
        # 完整 URL 为：BASE_URL + "/login"
        return self.goto("login")
    
    def login(self, username: str, password: str):
        """
        执行登录操作
        :param username: 用户名
        :param password: 密码
        :return: 返回 self，支持链式调用
        """
        # 步骤 1: 在用户名输入框中填写用户名
        # 使用父类继承的 fill 方法
        self.fill(self.USERNAME_INPUT, username)
        
        # 步骤 2: 在密码输入框中填写密码
        self.fill(self.PASSWORD_INPUT, password)
        
        # 步骤 3: 点击登录按钮
        self.click(self.LOGIN_BUTTON)
        
        # 返回 self，支持链式调用
        return self
    
    def get_error_message(self) -> str:
        """
        获取登录错误消息
        :return: 错误消息文本
        """
        # 调用父类继承的 get_text 方法获取错误消息元素的文本
        return self.get_text(self.ERROR_MESSAGE)
    
    def is_login_successful(self) -> bool:
        """
        检查登录是否成功
        :return: 如果登录成功返回 True，否则返回 False
        """
        # 调用父类继承的 is_visible 方法检查成功消息是否显示
        # 如果成功消息可见，说明登录成功
        return self.is_visible(self.SUCCESS_MESSAGE)


class HomePage(BasePage):
    """
    首页页面对象类
    封装首页的所有元素和操作
    继承自 BasePage，自动拥有所有通用操作方法
    """
    
    # ============================================
    # 元素定位器（类常量）
    # ============================================
    
    # 欢迎消息元素的 CSS 选择器
    WELCOME_MESSAGE = ".welcome"
    
    # 退出登录按钮的 CSS 选择器
    LOGOUT_BUTTON = "#logout-btn"
    
    def __init__(self, page: Page):
        """
        初始化首页页面对象
        :param page: Playwright 的 Page 对象
        """
        # 调用父类 BasePage 的构造函数
        super().__init__(page)
    
    def is_welcome_displayed(self) -> bool:
        """
        检查欢迎消息是否显示
        :return: 如果欢迎消息可见返回 True，否则返回 False
        """
        # 调用父类继承的 is_visible 方法检查欢迎消息元素
        return self.is_visible(self.WELCOME_MESSAGE)
    
    def logout(self):
        """
        执行退出登录操作
        :return: 返回 self，支持链式调用
        """
        # 点击退出登录按钮
        self.click(self.LOGOUT_BUTTON)
        
        # 返回 self，支持链式调用
        return self
