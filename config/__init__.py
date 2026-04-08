# 配置管理
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "config" / ".env"

# 加载环境变量
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv(BASE_DIR / "config" / ".env.example")


class Config:
    """测试配置类"""
    
    # 基础配置
    BASE_URL = os.getenv("BASE_URL", "https://example.com")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "100"))
    TIMEOUT = int(os.getenv("TIMEOUT", "30000"))
    
    # 浏览器配置
    BROWSER = os.getenv("BROWSER", "chromium")
    VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", "1920"))
    VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", "1080"))
    
    # 报告目录
    REPORT_DIR = BASE_DIR / "reports"
    SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"
    VIDEO_DIR = BASE_DIR / "reports" / "videos"
    
    # 确保目录存在
    REPORT_DIR.mkdir(exist_ok=True)
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)


config = Config()
