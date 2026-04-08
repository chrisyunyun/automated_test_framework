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
        page.goto("https://the-internet.herokuapp.com/login")
        page.fill("#username", "tomsmith")
        page.fill("#password", "supersecret")
        page.click('button[type="submit"]')
        
        # 验证登录成功消息
        expect(page.locator("#flash")).to_contain_text("You logged into a secure area")
        expect(page).to_have_url("https://the-internet.herokuapp.com/secure")
    
    @pytest.mark.smoke
    def test_login_invalid(self, page: Page):
        """测试无效登录"""
        page.goto("https://the-internet.herokuapp.com/login")
        page.fill("#username", "invalid")
        page.fill("#password", "invalid")
        page.click('button[type="submit"]')
        
        # 验证错误消息
        expect(page.locator("#flash")).to_contain_text("Invalid username")
    
    @pytest.mark.ui
    def test_page_elements(self, page: Page):
        """测试页面元素显示"""
        page.goto("https://the-internet.herokuapp.com/login")
        
        expect(page.locator("#username")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
