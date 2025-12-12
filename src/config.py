"""
数据库配置模块

从环境变量或配置文件读取数据库连接信息。
"""
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    # 如果没有安装python-dotenv，使用简单的实现
    def load_dotenv(dotenv_path=None):
        """简单的.env文件加载实现"""
        if dotenv_path is None:
            project_root = Path(__file__).parent.parent
            dotenv_path = project_root / "database" / ".env"
        
        env_file = Path(dotenv_path)
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()


# 加载.env文件
project_root = Path(__file__).parent.parent
env_path = project_root / "database" / ".env"
load_dotenv(env_path)


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        """初始化数据库配置"""
        self.host = os.getenv('DOLT_HOST', 'localhost')
        self.port = int(os.getenv('DOLT_PORT', '13306'))
        self.user = os.getenv('DOLT_USER', 'root')
        self.password = os.getenv('DOLT_ROOT_PASSWORD', 'test')
        self.database = os.getenv('DOLT_DATABASE', 'a_stock')
        self.charset = os.getenv('DOLT_CHARSET', 'utf8mb4')
    
    def get_connection_params(self) -> dict:
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
            f"DatabaseConfig(host={self.host}, port={self.port}, "
            f"user={self.user}, database={self.database})"
        )


# 全局配置实例
db_config = DatabaseConfig()

