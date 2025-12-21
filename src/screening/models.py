"""
选股数据模型

定义选股相关的数据模型。
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScreeningResult:
    """选股结果"""
    code: str
    name: str
    market: Optional[str] = None
    # 可以添加更多字段
