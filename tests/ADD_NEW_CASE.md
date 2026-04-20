# 新增测试用例指南

本文档说明如何在项目中新增一个测试用例。

---

## 一、编写测试代码

在对应的测试文件中新增用例，**docstring 格式必须正确**：

```python
@pytest.mark.smoke  # 或 @pytest.mark.regression
def test_ftxxx_your_case_name(self, page):
    """LOGIN-FT-xxx: 中文用例名称"""
    # 测试代码...
    assert condition, "失败时的提示信息"
```

### docstring 格式要求

```
LOGIN-FT-xxx: 中文用例名称
^^^ ^^^^^^^^^
│    │
│    └── 中文名称（前端显示）
│
└────── 用例 ID（必须唯一，建议按顺序编号）
```

### marker 说明

| marker | 用途 | 说明 |
|--------|------|------|
| `@pytest.mark.smoke` | 冒烟测试 | 核心功能，每次提交前必跑 |
| `@pytest.mark.regression` | 回归测试 | 完整功能测试，发布前执行 |

### 代码规范

```python
# ✅ 正确示例
def test_ft012_login_remember(self, browser):
    """LOGIN-FT-012: 勾选记住登录状态，重新打开系统时应直接进入工作台"""
    page.goto("/login")
    page.click(".remember-me")
    page.fill("input[name=account]", "13800138000")
    page.fill("input[name=password]", "password123")
    page.click("button[type=submit]")
    page.wait_for_url("**/dashboard")
    assert page.is_visible(".user-avatar")

# ❌ 错误示例（docstring 没有冒号）
def test_ft012_login_remember(self):
    """LOGIN-FT-012"""
    ...

# ❌ 错误示例（缺少 docstring）
def test_ft012_login_remember(self):
    page.goto("/login")
    ...
```

---

## 二、更新测试用例文档

打开 `tests/TEST_CASES.md`，在对应章节下添加：

```markdown
### LOGIN-FT-xxx | 中文用例名称
- **标记**: smoke
- **前置条件**: 已登录 OA 系统（若是登录相关用例则无）
- **测试步骤**:
  1. 打开登录页
  2. 输入账号密码
  3. 点击登录
- **预期结果**: 跳转至 dashboard 页面
```

同时更新统计表格：

```markdown
| 分类 | 数量 |
|------|------|
| smoke（冒烟测试） | 8 |
| regression（回归测试） | 5 |
| **总计** | **13** |
```

---

## 三、重启后端服务

```bash
# 在项目根目录执行
cd d:\GIT\pytest
python -m uvicorn server.main:app --reload --port 8000
```

后端热重载后，新用例会自动出现在前端页面上。

---

## 四、验证

1. 打开前端 http://localhost:3000
2. 检查新用例是否出现在列表中
3. 勾选新用例，点击"运行测试"
4. 检查执行结果是否正常

---

## 五、提交代码

```bash
git add tests/test_oa_login.py tests/TEST_CASES.md
git commit -m "新增 LOGIN-FT-xxx 用例: 中文用例名称"
git push
```

---

## 常见问题

### Q: docstring 格式不对会怎样？
A: 前端会显示函数名而不是中文名称，例如显示 `test Ftxxx Your Case Name`

### Q: 忘记更新 TEST_CASES.md 会有问题吗？
A: 不影响代码运行，但文档和实际用例不同步，统计数字会不准确

### Q: 可以新增测试文件吗？
A: 可以。新建文件后，后端会自动扫描 `tests/test_*.py` 模式的文件

### Q: marker 写错了会怎样？
A: 默认会被识别为 `regression`，不影响执行
