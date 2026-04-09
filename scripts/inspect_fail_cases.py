"""探查各种登录失败场景的提示文字"""
from playwright.sync_api import sync_playwright


def test_scenario(browser, account, password, label):
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()
    page.goto('https://192.168.16.4:8900/#/login', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=8000)

    if account is not None:
        page.fill('input[name=account]', account)
    if password is not None:
        page.fill('input[name=password]', password)

    page.click('button.el-button--primary')
    page.wait_for_timeout(3000)

    url = page.url
    msgs = []
    for sel in [
        '.el-message__content',
        '.el-message',
        '.el-form-item__error',
        '[class*=error-msg]',
        '.el-notification__content',
    ]:
        for el in page.query_selector_all(sel):
            txt = el.text_content().strip()
            if txt and txt not in msgs:
                msgs.append(txt)

    print(f"\n[{label}]")
    print(f"  URL: {url}")
    print(f"  提示文字: {msgs}")
    page.screenshot(path=f'reports/screenshots/case_{label}.png')
    ctx.close()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    test_scenario(browser, '', 'kq520', '01_账号为空')
    test_scenario(browser, '蔡云江', '', '02_密码为空')
    test_scenario(browser, 'notexist_user_xyz', 'wrongpass123', '03_账号不存在')
    test_scenario(browser, '蔡云江', 'wrongpass123', '04_密码错误')

    # Enter 键登录
    ctx = browser.new_context(ignore_https_errors=True)
    page = ctx.new_page()
    page.goto('https://192.168.16.4:8900/#/login', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=8000)
    page.fill('input[name=account]', '蔡云江')
    page.fill('input[name=password]', 'kq520')
    page.focus('input[name=password]')
    page.keyboard.press('Enter')
    page.wait_for_timeout(3000)
    print(f"\n[Enter键登录] URL: {page.url}")
    ctx.close()

    browser.close()
    print("\n探查完成")
