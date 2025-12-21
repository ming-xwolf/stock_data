"""
财务指标选股条件实现

提供营收、利润、EPS等财务指标筛选条件。
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BaseCondition

logger = logging.getLogger(__name__)


class RevenueCondition(BaseCondition):
    """营收筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选营收范围内的股票
        
        参数：
            min_revenue: 最小营收（元）
            max_revenue: 最大营收（元）
            report_date: 报告日期（YYYY-MM-DD格式），默认最新报告期
        """
        min_revenue = self.params.get('min_revenue')
        max_revenue = self.params.get('max_revenue')
        report_date = self.params.get('report_date')
        
        if not stock_codes:
            return []
        
        if min_revenue is None and max_revenue is None:
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
            
            if min_revenue is not None:
                conditions.append("total_revenue >= %s")
                params.append(min_revenue)
            if max_revenue is not None:
                conditions.append("total_revenue <= %s")
                params.append(max_revenue)
            
            if not conditions:
                return stock_codes
            
            # 如果指定了报告日期，使用指定日期；否则使用最新报告期
            if report_date:
                conditions.append("report_date = %s")
                params.append(report_date)
            else:
                # 使用最新报告期
                conditions.append("""
                    report_date = (
                        SELECT MAX(report_date) 
                        FROM stock_financial_income 
                        WHERE code = stock_financial_income.code
                    )
                """)
            
            sql = f"""
                SELECT DISTINCT code 
                FROM stock_financial_income 
                WHERE code = ANY(%s)
                AND {' AND '.join(conditions)}
            """
            params.insert(0, stock_codes)
            results = db_manager.execute_query(sql, tuple(params))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"营收筛选失败: {e}")
            return []


class ProfitCondition(BaseCondition):
    """利润筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选净利润范围内的股票
        
        参数：
            min_profit: 最小净利润（元）
            max_profit: 最大净利润（元）
            report_date: 报告日期（YYYY-MM-DD格式），默认最新报告期
            use_attributable: 是否使用归属于母公司所有者的净利润，默认True
        """
        min_profit = self.params.get('min_profit')
        max_profit = self.params.get('max_profit')
        report_date = self.params.get('report_date')
        use_attributable = self.params.get('use_attributable', True)
        
        if not stock_codes:
            return []
        
        if min_profit is None and max_profit is None:
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
            
            profit_field = 'net_profit_attributable' if use_attributable else 'net_profit'
            
            if min_profit is not None:
                conditions.append(f"{profit_field} >= %s")
                params.append(min_profit)
            if max_profit is not None:
                conditions.append(f"{profit_field} <= %s")
                params.append(max_profit)
            
            if not conditions:
                return stock_codes
            
            # 如果指定了报告日期，使用指定日期；否则使用最新报告期
            if report_date:
                conditions.append("report_date = %s")
                params.append(report_date)
            else:
                # 使用最新报告期
                conditions.append("""
                    report_date = (
                        SELECT MAX(report_date) 
                        FROM stock_financial_income 
                        WHERE code = stock_financial_income.code
                    )
                """)
            
            sql = f"""
                SELECT DISTINCT code 
                FROM stock_financial_income 
                WHERE code = ANY(%s)
                AND {' AND '.join(conditions)}
            """
            params.insert(0, stock_codes)
            results = db_manager.execute_query(sql, tuple(params))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"利润筛选失败: {e}")
            return []


class EPSCondition(BaseCondition):
    """每股收益筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选每股收益范围内的股票
        
        参数：
            min_eps: 最小每股收益（元）
            max_eps: 最大每股收益（元）
            report_date: 报告日期（YYYY-MM-DD格式），默认最新报告期
            use_diluted: 是否使用稀释每股收益，默认False（使用基本每股收益）
        """
        min_eps = self.params.get('min_eps')
        max_eps = self.params.get('max_eps')
        report_date = self.params.get('report_date')
        use_diluted = self.params.get('use_diluted', False)
        
        if not stock_codes:
            return []
        
        if min_eps is None and max_eps is None:
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
            
            eps_field = 'diluted_eps' if use_diluted else 'basic_eps'
            
            if min_eps is not None:
                conditions.append(f"{eps_field} >= %s")
                params.append(min_eps)
            if max_eps is not None:
                conditions.append(f"{eps_field} <= %s")
                params.append(max_eps)
            
            if not conditions:
                return stock_codes
            
            # 如果指定了报告日期，使用指定日期；否则使用最新报告期
            if report_date:
                conditions.append("report_date = %s")
                params.append(report_date)
            else:
                # 使用最新报告期
                conditions.append("""
                    report_date = (
                        SELECT MAX(report_date) 
                        FROM stock_financial_income 
                        WHERE code = stock_financial_income.code
                    )
                """)
            
            sql = f"""
                SELECT DISTINCT code 
                FROM stock_financial_income 
                WHERE code = ANY(%s)
                AND {' AND '.join(conditions)}
            """
            params.insert(0, stock_codes)
            results = db_manager.execute_query(sql, tuple(params))
            
            return [r['code'] for r in results]
        except Exception as e:
            logger.error(f"每股收益筛选失败: {e}")
            return []


class GrowthRateCondition(BaseCondition):
    """增长率筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选增长率范围内的股票
        
        参数：
            metric: 指标类型，'revenue' (营收) 或 'profit' (净利润)
            min_growth: 最小增长率（如0.1表示10%）
            max_growth: 最大增长率
            period: 比较周期，'quarter' (季度) 或 'year' (年度)，默认'quarter'
        """
        metric = self.params.get('metric', 'revenue')
        min_growth = self.params.get('min_growth')
        max_growth = self.params.get('max_growth')
        period = self.params.get('period', 'quarter')
        
        if not stock_codes:
            return []
        
        if min_growth is None and max_growth is None:
            return stock_codes
        
        # 从上下文获取数据库管理器
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        try:
            # 确定指标字段
            if metric == 'revenue':
                field = 'total_revenue'
            elif metric == 'profit':
                field = 'net_profit_attributable'
            else:
                logger.warning(f"不支持的指标类型: {metric}")
                return []
            
            result_codes = []
            
            for code in stock_codes:
                try:
                    # 获取最近两个报告期的数据
                    if period == 'quarter':
                        # 季度比较：获取最近两个季度
                        sql = """
                            SELECT report_date, {field}
                            FROM stock_financial_income
                            WHERE code = %s
                            AND report_type IN ('季报', '一季报', '中报', '三季报', '年报')
                            ORDER BY report_date DESC
                            LIMIT 2
                        """.format(field=field)
                    else:
                        # 年度比较：获取最近两个年度
                        sql = """
                            SELECT report_date, {field}
                            FROM stock_financial_income
                            WHERE code = %s
                            AND report_type = '年报'
                            ORDER BY report_date DESC
                            LIMIT 2
                        """.format(field=field)
                    
                    results = db_manager.execute_query(sql, (code,))
                    
                    if len(results) < 2:
                        continue
                    
                    current_value = results[0][field]
                    previous_value = results[1][field]
                    
                    if current_value is None or previous_value is None:
                        continue
                    if previous_value == 0:
                        continue
                    
                    # 计算增长率
                    growth_rate = (current_value - previous_value) / abs(previous_value)
                    
                    # 判断是否符合条件
                    if min_growth is not None and growth_rate < min_growth:
                        continue
                    if max_growth is not None and growth_rate > max_growth:
                        continue
                    
                    result_codes.append(code)
                    
                except Exception as e:
                    logger.debug(f"计算股票 {code} 增长率失败: {e}")
                    continue
            
            return result_codes
        except Exception as e:
            logger.error(f"增长率筛选失败: {e}")
            return []
