"""
易威行 OA 系统 — 登录功能测试
用例来源: 表格_20260409.csv（LOGIN-FT-001 ~ LOGIN-FT-010）

测试账号: 蔡云江 / kq520
测试地址: https://192.168.16.4:8900/#/login

注意:
  - LOGIN-FT-009（连续5次错误锁定账号）会污染账号状态，放在最后执行
  - LOGIN-FT-006（记住登录状态）需要关闭/重开浏览器，用独立 context 模拟
"""
import pytest
from playwright.sync_api import Page, expect

from pages.oa_login_page import OALoginPage
from config import config

# ── 测试账号常量 ──────────────────────────────────────────────
VALID_ACCOUNT  = config.OA_ACCOUNT
VALID_PASSWORD = config.OA_PASSWORD
WRONG_ACCOUNT  = 'notexist_user_xyz'
WRONG_PASSWORD = 'wrongpass_abc999'


@pytest.fixture
def login_page_oa(page: Page) -> OALoginPage:
    """创建 OA 登录页对象并导航到登录页"""
    lp = OALoginPage(page)
    lp.navigate()
    return lp


class TestOALogin:
    """易威行 OA 登录功能测试 (LOGIN-FT-001 ~ LOGIN-FT-010)"""

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-001  正确账号密码登录成功
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft001_login_success(self, login_page_oa: OALoginPage):
        """LOGIN-FT-001: 正确账号密码登录成功"""
        login_page_oa.login(VALID_ACCOUNT, VALID_PASSWORD)

        # 断言1: URL 跳转至 dashboard
        assert login_page_oa.is_login_success(), \
            "登录失败：未跳转至 dashboard 页面"

        # 断言2: 页面显示当前用户名
        avatar_text = login_page_oa.get_avatar_text()
        assert VALID_ACCOUNT in avatar_text, \
            f"登录成功但未显示用户名，实际显示: {avatar_text!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-002  手机号为空点击登录
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft002_empty_account(self, login_page_oa: OALoginPage):
        """LOGIN-FT-002: 手机号为空点击登录，应提示并停留在登录页"""
        login_page_oa.fill_password(VALID_PASSWORD).click_login()

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "空账号时不应跳转，但发生了页面跳转"

        # 断言2: 出现提示文字
        msg = login_page_oa.get_error_message()
        assert '手机号码' in msg or '账号' in msg or '用户' in msg, \
            f"未出现账号为空的提示，实际提示: {msg!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-003  密码为空点击登录
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft003_empty_password(self, login_page_oa: OALoginPage):
        """LOGIN-FT-003: 密码为空点击登录，应提示并停留在登录页"""
        login_page_oa.fill_account(VALID_ACCOUNT).click_login()

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "空密码时不应跳转，但发生了页面跳转"

        # 断言2: 出现提示文字
        msg = login_page_oa.get_error_message()
        assert '密码' in msg, \
            f"未出现密码为空的提示，实际提示: {msg!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-004  输入错误账号登录
    # ────────────────────────────────────────────────────────────
    @pytest.mark.regression
    def test_ft004_wrong_account(self, login_page_oa: OALoginPage):
        """LOGIN-FT-004: 输入不存在的账号，应提示错误并停留在登录页"""
        login_page_oa.login(WRONG_ACCOUNT, VALID_PASSWORD)

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "错误账号时不应跳转，但发生了页面跳转"

        # 断言2: 提示不泄露"账号错误"或"密码错误"，只说"用户名或密码不正确"
        msg = login_page_oa.get_error_message()
        assert len(msg) > 0, "应有登录失败提示，但未获取到任何提示文字"
        assert '用户名或密码不正确' in msg or '不正确' in msg or '错误' in msg, \
            f"错误提示内容不符合预期，实际: {msg!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-005  输入错误密码登录
    # ────────────────────────────────────────────────────────────
    @pytest.mark.regression
    def test_ft005_wrong_password(self, login_page_oa: OALoginPage):
        """LOGIN-FT-005: 正确账号 + 错误密码，应提示错误并停留在登录页"""
        login_page_oa.login(VALID_ACCOUNT, WRONG_PASSWORD)

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "错误密码时不应跳转，但发生了页面跳转"

        # 断言2: 提示文字
        msg = login_page_oa.get_error_message()
        assert '用户名或密码不正确' in msg or '不正确' in msg or '错误' in msg, \
            f"错误提示内容不符合预期，实际: {msg!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-006  勾选"记住登录状态"
    # ────────────────────────────────────────────────────────────
    @pytest.mark.regression
    def test_ft006_remember_login(self, browser):
        """LOGIN-FT-006: 勾选记住登录状态，重新打开系统时应直接进入工作台（免登录）"""
        # --- 第一次登录：勾选记住状态 ---
        ctx1 = browser.new_context(ignore_https_errors=True)
        page1 = ctx1.new_page()
        lp1 = OALoginPage(page1)
        lp1.navigate()
        lp1.click_remember_login()
        lp1.login(VALID_ACCOUNT, VALID_PASSWORD)
        lp1.wait_login_success()
        # 保存 storage state（cookies + localStorage，含 token）
        state = ctx1.storage_state()
        ctx1.close()

        # --- 第二次：带 storage state 重新访问系统 ---
        ctx2 = browser.new_context(
            ignore_https_errors=True,
            storage_state=state
        )
        page2 = ctx2.new_page()
        lp2 = OALoginPage(page2)
        lp2.navigate()
        page2.wait_for_timeout(2000)

        final_url = page2.url
        ctx2.close()

        # 断言: 直接跳转到 dashboard（说明 token 有效，免登录成功）
        # 这是"记住登录状态"的预期行为——有效 token 下无需重新登录
        assert 'dashboard' in final_url or 'login' not in final_url, \
            f"记住登录状态后应免登录进入工作台，实际 URL: {final_url!r}"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-007  手机号格式错误（非 11 位）
    # ────────────────────────────────────────────────────────────
    @pytest.mark.regression
    def test_ft007_account_too_short(self, login_page_oa: OALoginPage):
        """LOGIN-FT-007: 输入 10 位手机号，应拦截登录并给出格式提示"""
        login_page_oa.login('138001380', VALID_PASSWORD)  # 9 位

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "格式错误的手机号时不应跳转"

        # 断言2: 出现格式相关提示（或通用的"用户名或密码不正确"）
        msg = login_page_oa.get_error_message()
        assert len(msg) > 0, \
            f"应有格式错误提示，但未获取到任何提示文字"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-008  手机号含非数字字符
    # ────────────────────────────────────────────────────────────
    @pytest.mark.regression
    def test_ft008_account_non_numeric(self, login_page_oa: OALoginPage):
        """LOGIN-FT-008: 输入含字母的手机号，应拦截登录"""
        login_page_oa.login('1380013800a', VALID_PASSWORD)

        # 断言1: 仍在登录页
        assert login_page_oa.is_on_login_page(), \
            "含非数字字符的手机号时不应跳转"

        # 断言2: 出现提示
        msg = login_page_oa.get_error_message()
        assert len(msg) > 0, \
            f"应有格式错误提示，但未获取到任何提示文字"

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-010  回车键登录功能（放在锁定用例前）
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft010_enter_key_login(self, login_page_oa: OALoginPage):
        """LOGIN-FT-010: 密码框按 Enter 键应触发登录并跳转至首页"""
        login_page_oa.login_by_enter(VALID_ACCOUNT, VALID_PASSWORD)

        assert login_page_oa.is_login_success(), \
            "Enter 键登录失败：未跳转至 dashboard 页面"




