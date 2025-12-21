"""
基础选股条件实现

提供市场、行业、市值等基础筛选条件。
"""
import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from .base import BaseCondition

logger = logging.getLogger(__name__)


class MarketCondition(BaseCondition):
    """市场筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选指定市场的股票
        
        参数：
            market: 市场代码，'SH' 或 'SZ'
        """
        market = self.params.get('market')
        if not market:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 从上下文获取数据库管理器，如果没有则导入
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            # 从数据库查询指定市场的股票
            sql = "SELECT code FROM stocks WHERE market = %s"
            results = db_manager.execute_query(sql, (market,))
            market_stocks = {r['code'] for r in results}
            
            # 返回交集
            return [code for code in stock_codes if code in market_stocks]
        except Exception as e:
            logger.error(f"市场筛选失败: {e}")
            return []


class MarketValueCondition(BaseCondition):
    """市值筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选市值范围内的股票
        
        参数：
            min_value: 最小市值（元）
            max_value: 最大市值（元）
            use_total: 是否使用总市值，默认False（使用流通市值）
        """
        min_value = self.params.get('min_value')
        max_value = self.params.get('max_value')
        use_total = self.params.get('use_total', False)
        
        if not stock_codes:
            return []
        
        if min_value is None and max_value is None:
            return stock_codes
        
        # 从上下文获取数据库管理器
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            market_cap_field = 'total_market_cap' if use_total else 'circulating_market_cap'
            
            if min_value is not None:
                conditions.append(f"{market_cap_field} >= %s")
                params.append(min_value)
            if max_value is not None:
                conditions.append(f"{market_cap_field} <= %s")
                params.append(max_value)
            
            if not conditions:
                return stock_codes
            
            # 查询符合条件的股票（使用最新市值数据）
            sql = f"""
                SELECT DISTINCT code 
                FROM stock_market_value 
                WHERE code = ANY(%s)
                AND {' AND '.join(conditions)}
                AND update_date = (
                    SELECT MAX(update_date) 
                    FROM stock_market_value 
                    WHERE code = stock_market_value.code
                )
            """
            params.insert(0, stock_codes)
            results = db_manager.execute_query(sql, tuple(params))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"市值筛选失败: {e}")
            return []


class IndustryCondition(BaseCondition):
    """行业筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选指定行业的股票
        
        参数：
            industry_name: 行业名称
            industry_code: 行业代码（可选）
        """
        industry_name = self.params.get('industry_name')
        industry_code = self.params.get('industry_code')
        
        if not industry_name and not industry_code:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 从上下文获取数据库管理器
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if industry_name:
                conditions.append("industry_name = %s")
                params.append(industry_name)
            if industry_code:
                conditions.append("industry_code = %s")
                params.append(industry_code)
            
            sql = f"SELECT code FROM stock_industry WHERE {' AND '.join(conditions)}"
            results = db_manager.execute_query(sql, tuple(params))
            industry_stocks = {r['code'] for r in results}
            
            return [code for code in stock_codes if code in industry_stocks]
        except Exception as e:
            logger.error(f"行业筛选失败: {e}")
            return []


class ListDateCondition(BaseCondition):
    """上市日期筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选上市日期范围内的股票
        
        参数：
            min_date: 最小上市日期（YYYY-MM-DD格式）
            max_date: 最大上市日期（YYYY-MM-DD格式）
        """
        min_date = self.params.get('min_date')
        max_date = self.params.get('max_date')
        
        if not stock_codes:
            return []
        
        if min_date is None and max_date is None:
            return stock_codes
        
        # 从上下文获取数据库管理器
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if min_date is not None:
                conditions.append("list_date >= %s")
                params.append(min_date)
            if max_date is not None:
                conditions.append("list_date <= %s")
                params.append(max_date)
            
            if not conditions:
                return stock_codes
            
            sql = f"""
                SELECT code FROM stocks 
                WHERE code = ANY(%s)
                AND list_date IS NOT NULL
                AND {' AND '.join(conditions)}
            """
            params.insert(0, stock_codes)
            results = db_manager.execute_query(sql, tuple(params))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"上市日期筛选失败: {e}")
            return []


class CompanyTypeCondition(BaseCondition):
    """企业性质筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选指定企业性质的股票
        
        参数：
            company_type: 企业性质（如：央企国资控股、民企、外资等）
        """
        company_type = self.params.get('company_type')
        if not company_type:
            return stock_codes
        
        if not stock_codes:
            return []
        
        # 从上下文获取数据库管理器
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            sql = "SELECT code FROM stocks WHERE company_type = %s AND code = ANY(%s)"
            results = db_manager.execute_query(sql, (company_type, stock_codes))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"企业性质筛选失败: {e}")
            return []


class CodeListCondition(BaseCondition):
    """股票代码列表筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选指定股票代码列表
        
        参数：
            codes: 股票代码列表
            exclude: 是否排除这些代码，默认False（包含）
        """
        codes = self.params.get('codes', [])
        exclude = self.params.get('exclude', False)
        
        if not codes:
            return stock_codes if not exclude else []
        
        code_set = set(codes)
        
        if exclude:
            # 排除指定代码
            return [code for code in stock_codes if code not in code_set]
        else:
            # 只保留指定代码
            return [code for code in stock_codes if code in code_set]
