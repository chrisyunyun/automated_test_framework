"""
tests/ 目录的 conftest.py
覆盖 pytest-playwright 插件的 browser_context_args，
使所有测试忽略自签名 HTTPS 证书错误。
"""
import pytest
from config import config


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """覆盖 pytest-playwright 的 context 参数，忽略 HTTPS 证书错误"""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {
            "width": config.VIEWPORT_WIDTH,
            "height": config.VIEWPORT_HEIGHT,
        },
    }
