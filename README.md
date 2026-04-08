# Pytest + Playwright 自动化测试框架

简洁高效的 UI 自动化测试框架，基于 Python + Pytest + Playwright。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境
编辑 `config/.env` 文件：
```env
BASE_URL=https://example.com
HEADLESS=true
BROWSER=chromium
TIMEOUT=30000
```

### 3. 运行测试
```bash
# 运行所有测试
pytest

# 运行冒烟测试
pytest -m smoke

# 生成 HTML 报告
pytest --html=reports/report.html --self-contained-html

# 查看详细输出
pytest -v -s
```

## 📁 项目结构

```
automated_test_framework/
├── config/              # 配置管理
│   ├── __init__.py      # 配置类（加载.env 文件）
│   └── .env             # 环境变量配置
├── pages/               # Page Object 页面类
│   ├── __init__.py
│   ├── base_page.py     # 页面基类（通用操作）
│   └── login_page.py    # 登录页面示例
├── fixtures/            # Pytest fixtures
│   ├── __init__.py
│   └── conftest.py      # 浏览器/页面 fixtures
├── tests/               # 测试用例
│   ├── __init__.py
│   └── test_demo.py     # 示例测试
├── reports/             # 测试报告（自动生成）
├── pytest.ini           # Pytest 配置
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 💡 核心特性

- **Page Object 模式**：页面元素与测试逻辑分离
- **智能等待**：Playwright 自动等待元素就绪
- **Fixture 管理**：自动管理浏览器生命周期
- **测试标记**：smoke/regression/ui 分类执行
- **HTML 报告**：自动生成可视化测试报告
- **并行执行**：支持多进程加速测试

## 📝 编写测试示例

### 基础测试
```python
import pytest
from playwright.sync_api import Page, expect

class TestExample:
    
    @pytest.mark.smoke
    def test_baidu(self, page: Page):
        """测试百度首页"""
        page.goto("https://www.baidu.com")
        expect(page).to_have_title("百度一下，你就知道")
```

### 使用 Page Object
```python
from pages.login_page import LoginPage

class TestLogin:
    
    def test_login(self, login_page: LoginPage):
        login_page.navigate()
        login_page.login("user", "pass")
```

### 参数化测试
```python
@pytest.mark.parametrize("user,pwd", [
    ("user1", "pass1"),
    ("user2", "pass2"),
])
def test_multiple(user, pwd, page):
    page.goto("https://example.com/login")
    page.fill("#user", user)
    page.fill("#pass", pwd)
```

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `pytest` | 运行所有测试 |
| `pytest -m smoke` | 运行冒烟测试 |
| `pytest -m regression` | 运行回归测试 |
| `pytest -n 4` | 4 进程并行执行 |
| `pytest --html=report.html` | 生成 HTML 报告 |
| `pytest -v -s` | 详细输出模式 |
| `pytest tests/test_demo.py` | 运行指定测试文件 |

## 📖 代码说明

### 1. 配置管理 (`config/__init__.py`)
- 自动加载 `.env` 文件
- 提供全局配置对象 `config`

### 2. 页面基类 (`pages/base_page.py`)
- 封装常用操作：`click`, `fill`, `goto`, `screenshot`
- 支持链式调用
- 统一超时管理

### 3. Fixtures (`fixtures/conftest.py`)
- `browser`: 浏览器实例（session 级）
- `context`: 浏览器上下文（function 级）
- `page`: 页面对象（function 级）
- `login_page`: 登录页面对象

### 4. 测试用例
- 使用 `@pytest.mark` 标记分类
- 使用 `expect` 进行智能断言
- 支持参数化测试

## ⚠️ 注意事项

1. 首次运行需执行 `playwright install chromium` 下载浏览器
2. 测试失败截图保存在 `reports/screenshots/`
3. 修改 `config/.env` 可切换测试环境
4. 使用 `HEADLESS=false` 可查看浏览器执行过程
5. 如网络无法访问测试网站，请替换为本地可访问的 URL

## 🔗 相关资源

- [Pytest 文档](https://docs.pytest.org/)
- [Playwright 文档](https://playwright.dev/python/)
- [Page Object 模式](https://martinfowler.com/bliki/PageObject.html)

---

**更多帮助**: `pytest --help`
