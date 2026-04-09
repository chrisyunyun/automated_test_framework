"""
易威行 OA 系统 — 登录页面对象
目标: https://192.168.16.4:8900/#/login

元素结构（已通过 Playwright 探查确认）:
  - 账号输入框: input[name=account]  placeholder="请输入手机号码"
  - 密码输入框: input[name=password] placeholder="请输入登录密码"
  - 登录按钮:   button.el-button--primary
  - 记住登录:   .el-checkbox.el-checkbox--small
  - 错误提示:   .el-message__content (toast 形式)
  - 表单验证:   .el-form-item__error

登录成功标志:
  - URL 跳转至 #/dashboard
  - [class*=avatar] 元素显示用户名
"""
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class OALoginPage(BasePage):
    """易威行 OA 登录页面"""

    # ── 元素选择器 ────────────────────────────────────────────
    ACCOUNT_INPUT   = 'input[name=account]'
    PASSWORD_INPUT  = 'input[name=password]'
    LOGIN_BUTTON    = 'button.el-button--primary'
    REMEMBER_CHECK  = '.el-checkbox.el-checkbox--small'
    # 提示信息（toast 和表单两种形式）
    TOAST_MSG       = '.el-message__content'
    FORM_ERROR      = '.el-form-item__error'
    # 登录成功后标志
    AVATAR          = '[class*=avatar]'

    def __init__(self, page: Page):
        super().__init__(page)

    # ── 导航 ──────────────────────────────────────────────────
    def navigate(self):
        """打开登录页"""
        self.page.goto(self.base_url, timeout=self.timeout)
        self.page.wait_for_load_state('networkidle', timeout=self.timeout)
        return self

    # ── 操作 ──────────────────────────────────────────────────
    def fill_account(self, account: str):
        self.fill(self.ACCOUNT_INPUT, account)
        return self

    def fill_password(self, password: str):
        self.fill(self.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(self.LOGIN_BUTTON)
        return self

    def press_enter_to_login(self):
        """密码框聚焦后按 Enter 触发登录"""
        self.page.focus(self.PASSWORD_INPUT)
        self.page.keyboard.press('Enter')
        return self

    def click_remember_login(self):
        """勾选【记住登录状态】复选框"""
        self.page.locator(self.REMEMBER_CHECK).click()
        return self

    def login(self, account: str, password: str):
        """完整登录流程（填账号 + 填密码 + 点登录）"""
        self.fill_account(account)
        self.fill_password(password)
        self.click_login()
        return self

    def login_by_enter(self, account: str, password: str):
        """用 Enter 键触发登录"""
        self.fill_account(account)
        self.fill_password(password)
        self.press_enter_to_login()
        return self

    # ── 查询/断言辅助 ─────────────────────────────────────────
    def wait_login_success(self, timeout: int = 8000):
        """等待登录成功（URL 跳转到 dashboard）"""
        self.page.wait_for_url('**/#/dashboard', timeout=timeout)
        return self

    def is_login_success(self) -> bool:
        """判断是否登录成功（URL 包含 dashboard）"""
        try:
            self.page.wait_for_url('**/#/dashboard', timeout=6000)
            return True
        except Exception:
            return False

    def get_avatar_text(self) -> str:
        """获取登录后头像区域的用户名文字"""
        try:
            return self.page.locator(self.AVATAR).first.text_content(timeout=5000).strip()
        except Exception:
            return ''

    def get_toast_message(self, timeout: int = 4000) -> str:
        """获取 toast 提示文字（登录失败时的 el-message）"""
        try:
            loc = self.page.locator(self.TOAST_MSG).first
            loc.wait_for(timeout=timeout)
            return loc.text_content().strip()
        except Exception:
            return ''

    def get_form_error(self, timeout: int = 3000) -> str:
        """获取表单内联校验提示（空账号/密码时的 el-form-item__error）"""
        try:
            loc = self.page.locator(self.FORM_ERROR).first
            loc.wait_for(timeout=timeout)
            return loc.text_content().strip()
        except Exception:
            return ''

    def get_error_message(self, timeout: int = 4000) -> str:
        """智能获取当前页面上的错误提示（优先 toast，其次表单校验）"""
        msg = self.get_toast_message(timeout)
        if msg:
            return msg
        return self.get_form_error(timeout)

    def is_on_login_page(self) -> bool:
        """是否仍在登录页（未跳转）"""
        return '#/login' in self.page.url

    def get_account_value(self) -> str:
        """获取账号输入框当前值（用于测试"记住登录状态"）"""
        return self.page.locator(self.ACCOUNT_INPUT).input_value()
