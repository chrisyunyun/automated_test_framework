"""
易威行 OA 系统 — 导航功能测试
用例来源: LOGIN-FT-011 及后续非登录相关的功能用例

测试账号: 蔡云江 / kq520
测试地址: https://192.168.16.4:8900/#/login
"""
import pytest
from playwright.sync_api import Page

from pages.oa_login_page import OALoginPage
from config import config

VALID_ACCOUNT  = config.OA_ACCOUNT
VALID_PASSWORD = config.OA_PASSWORD


class TestOANavigation:
    """OA 导航功能测试集"""

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-011  首页快捷入口 → 产品管理
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft011_quick_entry_product_management(self, browser):
        """LOGIN-FT-011: 首页点击快捷入口→产品管理，应正确跳转到产品管理页面"""
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        lp = OALoginPage(page)

        # 步骤 1：登录成功
        lp.navigate()
        lp.login(VALID_ACCOUNT, VALID_PASSWORD)
        lp.wait_login_success()

        # 步骤 2：点击快捷入口中的「产品管理」
        page.locator('.quickItem', has_text='产品管理').click()

        # 步骤 3：等待页面跳转到产品管理路由
        page.wait_for_url('**/good/product/proMangement', timeout=8000)
        page.wait_for_load_state('networkidle', timeout=5000)

        # 断言 1：URL 包含产品管理路由
        assert '/good/product/proMangement' in page.url, \
            f"应跳转到产品管理页面，实际 URL: {page.url!r}"

        # 断言 2：左侧菜单「产品管理」处于选中态
        active_menu = page.locator('.el-menu-item.is-active', has_text='产品管理')
        assert active_menu.is_visible(), \
            "左侧菜单「产品管理」应处于选中状态"

        ctx.close()
