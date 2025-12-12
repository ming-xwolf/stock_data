"""
行业数据服务模块

提供股票行业信息的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional

from .db import db_manager

logger = logging.getLogger(__name__)


class IndustryService:
    """行业数据服务类"""
    
    INSERT_INDUSTRY_SQL = """
        INSERT INTO stock_industry (code, industry_name, industry_code, concept, area, update_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            industry_name = VALUES(industry_name),
            industry_code = VALUES(industry_code),
            concept = VALUES(concept),
            area = VALUES(area),
            update_date = VALUES(update_date),
            updated_at = CURRENT_TIMESTAMP
    """
    
    SELECT_INDUSTRY_SQL = "SELECT * FROM stock_industry WHERE code = %s"
    
    def insert_industry(self, code: str, industry_name: Optional[str] = None,
                       industry_code: Optional[str] = None, concept: Optional[str] = None,
                       area: Optional[str] = None, update_date: Optional[str] = None) -> bool:
        """
        插入或更新股票行业信息
        
        Args:
            code: 股票代码
            industry_name: 行业名称
            industry_code: 行业代码
            concept: 概念板块
            area: 地区
            update_date: 更新日期（YYYY-MM-DD格式）
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_INDUSTRY_SQL,
                (code, industry_name, industry_code, concept, area, update_date)
            )
            logger.debug(f"插入/更新股票 {code} 行业信息: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入股票 {code} 行业信息失败: {e}")
            return False
    
    def get_industry(self, code: str) -> Optional[Dict[str, any]]:
        """
        查询股票行业信息
        
        Args:
            code: 股票代码
            
        Returns:
            行业信息字典，如果不存在返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_INDUSTRY_SQL, (code,))
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"查询股票 {code} 行业信息失败: {e}")
            return None

