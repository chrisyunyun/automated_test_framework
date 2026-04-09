"""深度探查登录页行为"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()
    page.goto('https://192.168.16.4:8900/#/login', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=10000)

    # 捕获网络响应
    responses = []
    def on_response(response):
        if 'login' in response.url.lower() or response.status in [200, 400, 401, 403, 422]:
            responses.append({'url': response.url, 'status': response.status})
    page.on('response', on_response)

    # 测试1: 用账号蔡云江/kq520登录
    page.fill('input[name=account]', '蔡云江')
    page.fill('input[name=password]', 'kq520')
    page.screenshot(path='reports/screenshots/before_click.png')
    page.click('button.el-button--primary')
    page.wait_for_timeout(3000)

    print("登录后URL:", page.url)
    page.screenshot(path='reports/screenshots/after_login2.png', full_page=True)

    # 查找各种成功标志
    for sel in [
        '.el-menu', 'aside', '.sidebar', 'nav',
        '[class*=layout]', '[class*=home]', '[class*=dashboard]',
        '.el-avatar', '[class*=avatar]', '[class*=header]',
        '.el-breadcrumb', '[class*=menu]'
    ]:
        els = page.query_selector_all(sel)
        if els:
            txt = els[0].text_content().strip()[:60]
            print(f"  {sel}: {txt!r}")

    print("\n网络请求:", responses[:5])

    # 查找 toast/message 提示
    for sel in ['.el-message', '.el-notification', '[class*=message]', '[class*=toast]', '.el-alert__content']:
        els = page.query_selector_all(sel)
        if els:
            for el in els:
                print(f"  提示 {sel}: {el.text_content().strip()!r}")

    browser.close()
