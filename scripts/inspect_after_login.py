"""探查登录成功后页面结构"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()
    page.goto('https://192.168.16.4:8900/#/login', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=10000)

    # 用真实账号登录
    page.fill('input[name=account]', '蔡云江')
    page.fill('input[name=password]', 'kq520')
    page.click('button.el-button--primary')

    try:
        page.wait_for_url('**', timeout=8000)
        page.wait_for_load_state('networkidle', timeout=8000)
    except:
        pass

    page.screenshot(path='reports/screenshots/after_login.png', full_page=True)
    print("登录后URL:", page.url)
    print("登录后页面标题:", page.title())

    # 查找可能的欢迎/用户信息元素
    for sel in ['.user-name', '.username', '[class*=user]', '.avatar', '.el-dropdown', '.header', 'nav', '.sidebar']:
        els = page.query_selector_all(sel)
        if els:
            for el in els[:2]:
                txt = el.text_content().strip()[:80]
                print(f"  {sel}: {txt!r}")

    # 查找错误提示元素
    print("\n=== 可能的错误/提示元素 ===")
    for sel in ['.el-message', '.el-form-item__error', '[class*=error]', '[class*=tip]', '.el-alert']:
        els = page.query_selector_all(sel)
        if els:
            for el in els[:2]:
                print(f"  {sel}: {el.text_content().strip()!r}")

    browser.close()
    print("\n截图已保存")
