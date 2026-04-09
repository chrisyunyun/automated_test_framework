"""
Pytest Fixtures 配置
定义测试 fixtures，用于管理浏览器、上下文、页面等生命周期
Fixtures 是 pytest 的核心特性，用于测试初始化和资源管理
"""
# 导入 pytest 框架
import pytest
# 从 playwright 同步 API 导入所需的类型和工具
# sync_playwright: 启动 Playwright 的上下文管理器
# Page: 页面对象类型
# Browser: 浏览器对象类型
# BrowserContext: 浏览器上下文对象类型
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
# 导入配置模块，获取全局配置
from config import config


# ============================================
# 覆盖 pytest-playwright 插件的 context 参数
# 确保所有测试忽略 HTTPS 证书错误（内网自签名证书场景）
# ============================================

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {
            "width": config.VIEWPORT_WIDTH,
            "height": config.VIEWPORT_HEIGHT,
        },
    }


# ============================================
# Fixture 1: browser (浏览器实例)
# 作用域：session (整个测试会话只创建一次)
# ============================================

@pytest.fixture(scope="session")
def browser():
    """
    创建浏览器实例（会话级 fixture）
    整个测试会话期间只启动一次浏览器，所有测试共享
    :return: Playwright Browser 对象
    """
    # 使用 sync_playwright 上下文管理器启动 Playwright
    # 这会自动初始化 Playwright 引擎并加载浏览器驱动
    with sync_playwright() as p:
        # 根据配置文件中的 BROWSER 设置，动态获取浏览器类型
        # getattr(p, config.BROWSER) 等价于：
        #   - 如果 BROWSER="chromium"，则 p.chromium
        #   - 如果 BROWSER="firefox"，则 p.firefox
        #   - 如果 BROWSER="webkit"，则 p.webkit
        browser_type = getattr(p, config.BROWSER)
        
        # 启动浏览器实例
        # headless: 是否以无头模式运行（不显示浏览器界面）
        # slow_mo: 操作延迟时间（毫秒），用于调试时放慢操作
        browser = browser_type.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO
        )
        
        # yield 关键字将 browser 对象提供给测试用例使用
        # yield 之前的代码在测试开始前执行
        # yield 之后的代码在测试结束后执行（清理工作）
        yield browser
        
        # 测试会话结束后，关闭浏览器
        # 这是清理资源的重要步骤
        browser.close()


# ============================================
# Fixture 2: context (浏览器上下文)
# 作用域：function (每个测试函数创建一个新的上下文)
# ============================================

@pytest.fixture(scope="function")
def context(browser: Browser):
    """
    创建浏览器上下文（函数级 fixture）
    每个测试函数都有一个独立的上下文，实现测试隔离
    :param browser: 注入的 browser fixture
    :return: Playwright BrowserContext 对象
    """
    # 检查配置是否启用了录像功能
    if config.VIDEO == "on":
        # 如果启用录像，创建带录像功能的上下文
        # record_video_dir: 录像保存目录
        context = browser.new_context(
            # 设置视口大小（浏览器窗口大小）
            viewport={"width": config.VIEWPORT_WIDTH, "height": config.VIEWPORT_HEIGHT},
            # 忽略 HTTPS 证书错误（测试环境常用）
            ignore_https_errors=True,
            # 启用录像功能
            record_video_dir=str(config.VIDEO_DIR)
        )
    else:
        # 如果不启用录像，创建普通上下文
        context = browser.new_context(
            # 设置视口大小
            viewport={"width": config.VIEWPORT_WIDTH, "height": config.VIEWPORT_HEIGHT},
            # 忽略 HTTPS 证书错误
            ignore_https_errors=True
        )
    
    # 将上下文提供给测试用例使用
    yield context
    
    # 测试结束后，关闭上下文
    # 关闭上下文会自动关闭该上下文中的所有页面
    context.close()


# ============================================
# Fixture 3: page (页面对象)
# 作用域：function (每个测试函数创建一个新的页面)
# ============================================

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    创建页面对象（函数级 fixture）
    每个测试函数都有一个独立的页面，实现测试隔离
    :param context: 注入的 context fixture
    :return: Playwright Page 对象
    """
    # 在上下文中创建一个新的页面（标签页）
    page = context.new_page()
    
    # 设置页面的默认超时时间
    # 这个超时时间会应用于所有页面操作（点击、填充、导航等）
    page.set_default_timeout(config.TIMEOUT)
    
    # 将页面对象提供给测试用例使用
    yield page
    
    # 测试结束后，关闭页面
    # 关闭页面会释放相关资源
    page.close()



