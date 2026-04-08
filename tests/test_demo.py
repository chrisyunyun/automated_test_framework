"""
实际可运行的测试示例
使用 the-internet.herokuapp.com 演示测试编写
"""
import pytest
from playwright.sync_api import Page, expect


class TestLoginDemo:
    """登录功能测试示例"""
    
    @pytest.mark.smoke
    def test_login_success(self, page: Page):
        """测试登录成功"""
        page.goto("https://www.saucedemo.com/")
        page.get_by_role("textbox", name="用户名/邮箱").fill("admin")
        page.get_by_role("textbox", name="密码").fill("kq520123")
        page.get_by_role("button", name="登 录").click()
        dashboard_link = page.get_by_role("link", name="仪表盘")
        dashboard_link.wait_for(timeout=5000)  # 等待10秒，超时则失败
        assert dashboard_link.is_visible(), "登录失败：显示仪表盘子"


