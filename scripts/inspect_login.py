"""探查登录页面真实元素结构"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()
    page.goto('https://192.168.16.4:8900/#/login', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=10000)
    page.screenshot(path='reports/screenshots/login_page.png', full_page=True)

    print("=== INPUT 元素 ===")
    inputs = page.query_selector_all('input')
    for i, el in enumerate(inputs):
        t = el.get_attribute('type') or ''
        ph = el.get_attribute('placeholder') or ''
        nm = el.get_attribute('name') or ''
        eid = el.get_attribute('id') or ''
        cls = el.get_attribute('class') or ''
        print(f"input[{i}]: type={t!r} placeholder={ph!r} name={nm!r} id={eid!r} class={cls!r}")

    print("\n=== BUTTON 元素 ===")
    btns = page.query_selector_all('button')
    for i, el in enumerate(btns):
        txt = el.text_content().strip()
        cls = el.get_attribute('class') or ''
        print(f"button[{i}]: text={txt!r} class={cls!r}")

    print("\n=== 复选框 / checkbox ===")
    checks = page.query_selector_all('input[type=checkbox], .el-checkbox, [role=checkbox]')
    for i, el in enumerate(checks):
        txt = el.text_content().strip()
        cls = el.get_attribute('class') or ''
        print(f"checkbox[{i}]: text={txt!r} class={cls!r}")

    print("\n=== 页面标题 ===")
    print(page.title())

    browser.close()
    print("\n截图已保存: reports/screenshots/login_page.png")
