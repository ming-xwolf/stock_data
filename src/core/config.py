"""
数据库配置模块

从环境变量或配置文件读取 Supabase (PostgreSQL) 数据库连接信息。
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
            # 默认从项目根目录读取
            project_root = Path(__file__).parent.parent.parent
            dotenv_path = project_root / ".env"
        
        env_file = Path(dotenv_path)
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()


# 加载.env文件（从项目根目录读取）
project_root = Path(__file__).parent.parent.parent
root_env_path = project_root / ".env"
load_dotenv(root_env_path)

# 导入数据库适配器
from .db_adapters import SupabaseConfig


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        """初始化数据库配置，使用 Supabase"""
        self.db_type = 'supabase'
        self._config = SupabaseConfig()
    
    def get_connection_params(self) -> dict:
        """
        获取数据库连接参数字典
        
        Returns:
            包含连接参数的字典
        """
        return self._config.get_connection_params()
    
    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        return f"DatabaseConfig(type={self.db_type}, {self._config})"
    
    @property
    def config(self) -> SupabaseConfig:
        """
        获取底层配置对象
        
        Returns:
            SupabaseConfig 实例
        """
        return self._config


# 全局配置实例
db_config = DatabaseConfig()

