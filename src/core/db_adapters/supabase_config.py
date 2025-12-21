"""
Supabase (PostgreSQL) 数据库配置模块
"""
import os
from urllib.parse import urlparse
from typing import Optional, Dict


class SupabaseConfig:
    """Supabase (PostgreSQL) 数据库配置类"""
    
    def __init__(self):
        """初始化 Supabase 配置"""
        # 优先使用 URI 连接
        self.uri = os.getenv('SUPABASE_URI') or os.getenv('DATABASE_URL')
        
        # 如果没有 URI，则使用单独的连接参数
        if not self.uri:
            self.host = os.getenv('SUPABASE_HOST') or os.getenv('DB_HOST', 'localhost')
            self.port = int(os.getenv('SUPABASE_PORT') or os.getenv('DB_PORT', '5432'))
            self.user = os.getenv('SUPABASE_USER') or os.getenv('DB_USER', 'postgres')
            self.password = os.getenv('SUPABASE_PASSWORD') or os.getenv('DB_PASSWORD', '')
            self.database = os.getenv('SUPABASE_DATABASE') or os.getenv('DB_NAME', 'postgres')
        else:
            # 从 URI 解析参数（用于日志显示）
            parsed = urlparse(self.uri)
            self.host = parsed.hostname or 'localhost'
            self.port = parsed.port or 5432
            self.user = parsed.username or 'postgres'
            self.password = parsed.password or ''
            self.database = parsed.path.lstrip('/') if parsed.path else 'postgres'
    
    def get_connection_params(self) -> Dict:
        """
        获取数据库连接参数字典
        
        Returns:
            包含连接参数的字典
        """
        if self.uri:
            return {'uri': self.uri}
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
        }
    
    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        if self.uri:
            # 隐藏密码
            safe_uri = self.uri.split('@')[0] + '@***' if '@' in self.uri else self.uri
            return f"SupabaseConfig(uri={safe_uri})"
        return (
            f"SupabaseConfig(host={self.host}, port={self.port}, "
            f"user={self.user}, database={self.database})"
        )
