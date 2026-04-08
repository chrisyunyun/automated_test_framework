"""
Page Object Model (POM) 基类
提供所有页面类的通用操作方法
实现页面操作与测试逻辑的分离，提高代码可维护性
"""
# 从 playwright 同步 API 导入 Page 对象和 expect 断言工具
from playwright.sync_api import Page, expect
# 导入配置模块，获取全局配置信息
from config import config


class BasePage:
    """
    页面基类
    封装 Playwright 的常用操作，提供统一的页面操作接口
    所有具体页面类都应继承此类
    """
    
    def __init__(self, page: Page):
        """
        初始化基类
        :param page: Playwright 的 Page 对象，代表浏览器中的一个标签页
        """
        # 保存 page 对象实例，后续所有操作都基于此对象
        self.page = page
        
        # 从配置中获取基础 URL，用于页面导航
        self.base_url = config.BASE_URL
        
        # 从配置中获取默认超时时间，用于所有操作的超时控制
        self.timeout = config.TIMEOUT
        
    def goto(self, path: str = ""):
        """
        导航到指定页面
        :param path: URL 路径，如果为空则跳转到 BASE_URL
        :return: 返回 self，支持链式调用
        """
        # 如果提供了 path，则拼接完整 URL；否则使用基础 URL
        # 例如：path="login" -> "https://example.com/login"
        url = f"{self.base_url}/{path}" if path else self.base_url
        
        # 使用 Playwright 的 goto 方法导航到指定 URL
        # timeout 参数指定页面加载的最长等待时间
        self.page.goto(url, timeout=self.timeout)
        
        # 返回 self，支持链式调用，如：page.goto("login").fill(...).click(...)
        return self
    
    def click(self, selector: str):
        """
        点击页面元素
        :param selector: CSS 选择器或其他 Playwright 支持的选择器
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 click 方法点击元素
        # timeout 参数指定等待元素可点击的最长时间
        self.page.click(selector, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def fill(self, selector: str, value: str):
        """
        填充输入框（清空原有内容后填入新值）
        :param selector: 输入框的选择器
        :param value: 要填入的文本值
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 fill 方法填充输入框
        # fill 会先清空输入框再填入新值
        self.page.fill(selector, value, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def type_text(self, selector: str, value: str):
        """
        模拟键盘输入（逐字符输入，保留原有内容）
        :param selector: 输入框的选择器
        :param value: 要输入的文本值
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 type 方法模拟键盘输入
        # type 会逐字符输入，不会清空原有内容
        self.page.type(selector, value, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def get_text(self, selector: str) -> str:
        """
        获取元素的文本内容
        :param selector: 元素的选择器
        :return: 元素的文本内容字符串
        """
        # 使用 Playwright 的 text_content 方法获取元素文本
        # timeout 参数指定等待元素出现的最长时间
        return self.page.text_content(selector, timeout=self.timeout)
    
    def get_attribute(self, selector: str, attribute: str) -> str:
        """
        获取元素的指定属性值
        :param selector: 元素的选择器
        :param attribute: 属性名称，如 "href", "value", "class" 等
        :return: 属性值字符串
        """
        # 使用 Playwright 的 get_attribute 方法获取属性值
        return self.page.get_attribute(selector, attribute, timeout=self.timeout)
    
    def is_visible(self, selector: str) -> bool:
        """
        检查元素是否可见
        :param selector: 元素的选择器
        :return: 如果元素可见返回 True，否则返回 False
        """
        try:
            # 使用 Playwright 的 expect 断言检查元素是否可见
            # to_be_visible() 会等待元素变为可见状态
            # timeout=5000 表示最多等待 5 秒
            expect(self.page.locator(selector)).to_be_visible(timeout=5000)
            
            # 如果断言成功，说明元素可见
            return True
        except:
            # 如果断言失败（超时或元素不存在），说明元素不可见
            return False
    
    def is_enabled(self, selector: str) -> bool:
        """
        检查元素是否可用（未被禁用）
        :param selector: 元素的选择器
        :return: 如果元素可用返回 True，否则返回 False
        """
        try:
            # 使用 Playwright 的 expect 断言检查元素是否启用
            # to_be_enabled() 会等待元素变为可用状态
            expect(self.page.locator(selector)).to_be_enabled(timeout=5000)
            
            # 如果断言成功，说明元素可用
            return True
        except:
            # 如果断言失败，说明元素被禁用或不存在
            return False
    
    def wait_for_element(self, selector: str, state: str = "visible"):
        """
        等待元素达到指定状态
        :param selector: 元素的选择器
        :param state: 期望的状态，可选值："visible", "hidden", "attached", "detached"
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 wait_for_selector 方法等待元素
        # state 参数指定等待的状态：
        #   - "visible": 元素存在且可见
        #   - "hidden": 元素不存在或不可见
        #   - "attached": 元素存在于 DOM 中
        #   - "detached": 元素从 DOM 中移除
        self.page.wait_for_selector(selector, state=state, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def wait_for_url(self, url: str):
        """
        等待页面 URL 变为指定值
        :param url: 期望的 URL（支持通配符 **）
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 wait_for_url 方法等待 URL 变化
        # 支持通配符，例如："**/home" 匹配任何以 /home 结尾的 URL
        self.page.wait_for_url(url, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def screenshot(self, name: str):
        """
        截取当前页面截图
        :param name: 截图文件名（不含扩展名）
        :return: 返回 self，支持链式调用
        """
        # 构建截图文件完整路径：截图目录/文件名.png
        # config.SCREENSHOT_DIR 是配置中定义的截图保存目录
        screenshot_path = str(config.SCREENSHOT_DIR / f"{name}.png")
        
        # 使用 Playwright 的 screenshot 方法截取页面
        # path 参数指定截图保存路径
        self.page.screenshot(path=screenshot_path)
        
        # 返回 self，支持链式调用
        return self
    
    def hover(self, selector: str):
        """
        鼠标悬停在元素上
        :param selector: 元素的选择器
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 hover 方法模拟鼠标悬停
        self.page.hover(selector, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def select_option(self, selector: str, value: str):
        """
        选择下拉框选项
        :param selector: 下拉框的选择器
        :param value: 要选择的选项值
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 select_option 方法选择下拉选项
        self.page.select_option(selector, value, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def check(self, selector: str):
        """
        勾选复选框
        :param selector: 复选框的选择器
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 check 方法勾选复选框
        self.page.check(selector, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
    
    def uncheck(self, selector: str):
        """
        取消勾选复选框
        :param selector: 复选框的选择器
        :return: 返回 self，支持链式调用
        """
        # 使用 Playwright 的 uncheck 方法取消勾选
        self.page.uncheck(selector, timeout=self.timeout)
        
        # 返回 self，支持链式调用
        return self
