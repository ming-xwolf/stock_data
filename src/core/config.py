"""
数据库配置模块

从环境变量或配置文件读取数据库连接信息。
支持 Supabase (PostgreSQL) 和 Dolt (MySQL) 数据库。
默认使用 Supabase 数据库。
"""
import os
from pathlib import Path
from typing import Optional, Literal, Union

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


# 加载.env文件（优先从项目根目录读取）
project_root = Path(__file__).parent.parent.parent
root_env_path = project_root / ".env"
load_dotenv(root_env_path)

# 如果根目录没有 .env 文件，则尝试从 database/.env 读取（向后兼容）
if not root_env_path.exists():
    database_env_path = project_root / "database" / ".env"
    load_dotenv(database_env_path)

# 导入数据库适配器
from .db_adapters import SupabaseConfig, DoltConfig


class DatabaseConfig:
    """数据库配置类（统一接口）"""
    
    def __init__(self, db_type: Optional[Literal['supabase', 'dolt']] = None):
        """
        初始化数据库配置
        
        Args:
            db_type: 数据库类型，'supabase' 或 'dolt'。如果为 None，则从环境变量读取或默认使用 'supabase'
        """
        # 从环境变量读取数据库类型，默认为 'supabase'
        self.db_type = db_type or os.getenv('DB_TYPE', 'supabase').lower()
        
        # 根据类型创建对应的配置对象
        if self.db_type == 'supabase':
            self._config = SupabaseConfig()
        else:
            self._config = DoltConfig()
    
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
    def config(self) -> Union[SupabaseConfig, DoltConfig]:
        """
        获取底层配置对象
        
        Returns:
            SupabaseConfig 或 DoltConfig 实例
        """
        return self._config


# 全局配置实例（默认使用 Supabase）
db_config = DatabaseConfig()

