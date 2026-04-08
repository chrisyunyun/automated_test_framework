"""
工具类（精简版）
提供常用的数据读取和断言辅助
"""
import json
from datetime import datetime


class DataHelper:
    """数据读取辅助类"""
    
    @staticmethod
    def read_json(file_path: str) -> dict:
        """读取 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def generate_timestamp() -> str:
        """生成时间戳"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
