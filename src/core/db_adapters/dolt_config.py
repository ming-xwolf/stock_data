"""
Dolt (MySQL) 数据库配置模块
"""
import os
from typing import Dict


class DoltConfig:
    """Dolt (MySQL) 数据库配置类"""
    
    def __init__(self):
        """初始化 Dolt 配置"""
        self.host = os.getenv('DOLT_HOST', '192.168.2.37')
        self.port = int(os.getenv('DOLT_PORT', '13306'))
        self.user = os.getenv('DOLT_USER', 'root')
        self.password = os.getenv('DOLT_ROOT_PASSWORD', 'test')
        self.database = os.getenv('DOLT_DATABASE', 'a_stock')
        self.charset = os.getenv('DOLT_CHARSET', 'utf8mb4')
        self.uri = None
    
    def get_connection_params(self) -> Dict:
        """
        获取数据库连接参数字典
        
        Returns:
            包含连接参数的字典
        """
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': self.charset,
            'cursorclass': None,  # 可以在使用时指定
        }
    
    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        return (
            f"DoltConfig(host={self.host}, port={self.port}, "
            f"user={self.user}, database={self.database})"
        )
