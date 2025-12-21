"""
财务数据服务模块

提供股票财务数据的存储和查询功能。
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import financial_sql

logger = logging.getLogger(__name__)


class FinancialService:
    """财务数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_INCOME_SQL = sql_manager.get_sql(financial_sql, 'INSERT_INCOME')
        self.SELECT_INCOME_COUNT_SQL = sql_manager.get_sql(financial_sql, 'SELECT_INCOME_COUNT')
        self.SELECT_INCOME_DATES_SQL = sql_manager.get_sql(financial_sql, 'SELECT_INCOME_DATES')
        self.SELECT_LATEST_INCOME_SQL = sql_manager.get_sql(financial_sql, 'SELECT_LATEST_INCOME')
        self.SELECT_STOCKS_WITHOUT_REPORT_DATE_SQL = sql_manager.get_sql(financial_sql, 'SELECT_STOCKS_WITHOUT_REPORT_DATE')
    
    def insert_income_statement(self, code: str, report_date: str,
                               report_period: Optional[str] = None,
                               report_type: Optional[str] = None,
                               total_revenue: Optional[float] = None,
                               operating_revenue: Optional[float] = None,
                               operating_cost: Optional[float] = None,
                               operating_profit: Optional[float] = None,
                               total_profit: Optional[float] = None,
                               net_profit: Optional[float] = None,
                               net_profit_attributable: Optional[float] = None,
                               basic_eps: Optional[float] = None,
                               diluted_eps: Optional[float] = None) -> bool:
        """插入利润表数据"""
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_INCOME_SQL,
                (code, report_date, report_period, report_type,
                 total_revenue, operating_revenue, operating_cost,
                 operating_profit, total_profit, net_profit,
                 net_profit_attributable, basic_eps, diluted_eps)
            )
            logger.debug(f"插入利润表 {code}-{report_date}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入利润表失败: {e}")
            return False
    
    def get_income_statement_count(self, code: str) -> Dict[str, any]:
        """
        获取股票利润表数据统计信息
        
        Args:
            code: 股票代码
            
        Returns:
            包含 count（数据条数）和 latest_date（最新报告日期）的字典
        """
        try:
            results = db_manager.execute_query(self.SELECT_INCOME_COUNT_SQL, (code,))
            if results and len(results) > 0:
                result = results[0]
                latest_date = result.get('latest_date')
                if latest_date:
                    if isinstance(latest_date, datetime):
                        latest_date = latest_date.strftime('%Y-%m-%d')
                    elif not isinstance(latest_date, str):
                        latest_date = str(latest_date)
                return {
                    'count': result.get('count', 0),
                    'latest_date': latest_date
                }
            return {'count': 0, 'latest_date': None}
        except Exception as e:
            logger.error(f"查询股票 {code} 利润表统计信息失败: {e}")
            return {'count': 0, 'latest_date': None}
    
    def get_income_statement_dates(self, code: str) -> List[str]:
        """
        获取股票所有利润表报告日期列表
        
        Args:
            code: 股票代码
            
        Returns:
            报告日期列表（按日期降序排列）
        """
        try:
            results = db_manager.execute_query(self.SELECT_INCOME_DATES_SQL, (code,))
            dates = []
            for row in results:
                report_date = row.get('report_date')
                if report_date:
                    if isinstance(report_date, datetime):
                        dates.append(report_date.strftime('%Y-%m-%d'))
                    elif isinstance(report_date, str):
                        dates.append(report_date)
                    else:
                        dates.append(str(report_date))
            return dates
        except Exception as e:
            logger.error(f"查询股票 {code} 利润表报告日期失败: {e}")
            return []
    
    def has_complete_income_data(self, code: str, api_data: List[Dict[str, any]]) -> bool:
        """
        检查数据库中是否已有完整的利润表数据
        
        通过比较API返回的数据和数据库中的数据来判断：
        1. 如果数据库为空，返回False（需要更新）
        2. 如果API返回的所有报告日期都在数据库中，返回True（已完整）
        3. 如果API返回的数据中有数据库中没有的报告日期，返回False（需要更新）
        
        Args:
            code: 股票代码
            api_data: API返回的利润表数据列表
            
        Returns:
            如果数据已完整返回True，否则返回False
        """
        try:
            if not api_data:
                return False
            
            # 获取数据库中的报告日期
            db_dates = set(self.get_income_statement_dates(code))
            
            # 如果数据库为空，需要更新
            if not db_dates:
                return False
            
            # 获取API返回的所有报告日期
            api_dates = set()
            for item in api_data:
                report_date = item.get('report_date')
                if report_date:
                    api_dates.add(str(report_date))
            
            # 如果API返回的所有日期都在数据库中，说明数据已完整
            if api_dates.issubset(db_dates):
                logger.debug(f"股票 {code} 利润表数据已完整（API返回 {len(api_dates)} 期，数据库有 {len(db_dates)} 期），跳过更新")
                return True
            
            # 如果API返回的日期中有数据库没有的，需要更新
            missing_in_db = api_dates - db_dates
            if missing_in_db:
                logger.debug(f"股票 {code} 利润表数据不完整，数据库缺少 {len(missing_in_db)} 期数据，需要更新")
                return False
            
            return False
        except Exception as e:
            logger.error(f"检查股票 {code} 利润表数据完整性失败: {e}", exc_info=True)
            return False
    
    def get_latest_income_statement(self, code: str) -> Optional[Dict[str, any]]:
        """
        获取股票最新的利润表数据
        
        Args:
            code: 股票代码
            
        Returns:
            包含 report_date、report_period、report_type 的字典，如果没有数据返回None
        """
        try:
            results = db_manager.execute_query(self.SELECT_LATEST_INCOME_SQL, (code,))
            if results and len(results) > 0:
                result = results[0]
                report_date = result.get('report_date')
                if report_date:
                    if isinstance(report_date, datetime):
                        report_date = report_date.strftime('%Y-%m-%d')
                    elif not isinstance(report_date, str):
                        report_date = str(report_date)
                return {
                    'report_date': report_date,
                    'report_period': result.get('report_period'),
                    'report_type': result.get('report_type')
                }
            return None
        except Exception as e:
            logger.error(f"查询股票 {code} 最新利润表数据失败: {e}")
            return None
    
    def is_income_data_up_to_date(self, code: str) -> bool:
        """
        检查利润表数据是否是最新的（不调用API，仅检查数据库）
        
        判断逻辑：
        1. 如果数据库为空，返回False（需要更新）
        2. 获取数据库中的最新报告日期
        3. 根据当前日期和报告期规律判断数据是否已是最新
        4. 如果已是最新，返回True（跳过API调用）
        5. 否则返回False（需要调用API更新）
        
        报告期规律：
        - 一季报：报告日期为3月31日，通常在4月底前发布
        - 中报：报告日期为6月30日，通常在8月底前发布
        - 三季报：报告日期为9月30日，通常在10月底前发布
        - 年报：报告日期为12月31日，通常在次年4月底前发布
        
        判断规则（简化版）：
        - 如果最新报告日期是最近一个报告期，且当前时间还没到下一报告期发布时间，认为已是最新
        - 例如：最新是2024Q3（9月30日），现在是11月，2024Q4还没发布，认为已是最新
        - 例如：最新是2024Q3（9月30日），现在是1月，2024Q4应该已经发布了，需要更新
        
        更简单的判断：
        - 如果最新报告日期是最近3个月内的季度报告日期（3/6/9/12月），认为可能已是最新
        - 如果最新报告日期超过3个月，认为需要更新
        
        Args:
            code: 股票代码
            
        Returns:
            如果数据已是最新返回True，否则返回False
        """
        try:
            latest = self.get_latest_income_statement(code)
            if not latest or not latest.get('report_date'):
                return False
            
            latest_date_str = latest.get('report_date')
            if not latest_date_str:
                return False
            
            # 解析最新报告日期
            try:
                latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"股票 {code} 最新报告日期格式错误: {latest_date_str}")
                return False
            
            # 获取当前日期
            today = datetime.now().date()
            current_year = today.year
            current_month = today.month
            
            latest_year = latest_date.year
            latest_month = latest_date.month
            
            # 计算距离最新报告日期的月数
            months_diff = (current_year - latest_year) * 12 + (current_month - latest_month)
            
            # 如果最新报告日期超过6个月，肯定需要更新
            if months_diff > 6:
                logger.debug(f"股票 {code} 最新报告日期 {latest_date_str} 已超过6个月（{months_diff}个月），需要更新")
                return False
            
            # 如果最新报告日期是季度报告日期（3/6/9/12月），且是最近3个月内的，认为已是最新
            if latest_month in [3, 6, 9, 12] and months_diff <= 3:
                logger.debug(f"股票 {code} 最新报告日期 {latest_date_str} 是季度报告日期，且是最近3个月内的，认为已是最新")
                return True
            
            # 如果最新报告日期是最近3个月内的，但不是季度报告日期，也认为可能已是最新
            if months_diff <= 3:
                logger.debug(f"股票 {code} 最新报告日期 {latest_date_str} 是最近3个月内的，认为可能已是最新")
                return True
            
            # 如果最新报告日期是3-6个月前的，需要更新
            logger.debug(f"股票 {code} 最新报告日期 {latest_date_str} 是 {months_diff} 个月前的，需要更新")
            return False
            
        except Exception as e:
            logger.error(f"检查股票 {code} 利润表数据是否最新失败: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_previous_report_date() -> str:
        """
        计算上一个报告期的报告日期
        
        报告期规律：
        - 一季报：3月31日
        - 中报：6月30日
        - 三季报：9月30日
        - 年报：12月31日
        
        判断逻辑：
        - 如果当前是1-3月，上一个报告期是去年12月31日（年报）
        - 如果当前是4-6月，上一个报告期是今年3月31日（一季报）
        - 如果当前是7-9月，上一个报告期是今年6月30日（中报）
        - 如果当前是10-12月，上一个报告期是今年9月30日（三季报）
        
        Returns:
            上一个报告期的日期（YYYY-MM-DD格式）
        """
        today = datetime.now().date()
        current_year = today.year
        current_month = today.month
        
        if current_month in [1, 2, 3]:
            # 当前是1-3月，上一个报告期是去年12月31日（年报）
            previous_year = current_year - 1
            return f"{previous_year}-12-31"
        elif current_month in [4, 5, 6]:
            # 当前是4-6月，上一个报告期是今年3月31日（一季报）
            return f"{current_year}-03-31"
        elif current_month in [7, 8, 9]:
            # 当前是7-9月，上一个报告期是今年6月30日（中报）
            return f"{current_year}-06-30"
        else:  # current_month in [10, 11, 12]
            # 当前是10-12月，上一个报告期是今年9月30日（三季报）
            return f"{current_year}-09-30"
    
    def get_stocks_without_report_date(self, report_date: str) -> List[str]:
        """
        查询没有指定报告日期的股票代码列表
        
        Args:
            report_date: 报告日期（YYYY-MM-DD格式）
            
        Returns:
            股票代码列表
        """
        try:
            results = db_manager.execute_query(
                self.SELECT_STOCKS_WITHOUT_REPORT_DATE_SQL,
                (report_date,)
            )
            codes = []
            for row in results:
                code = row.get('code')
                if code:
                    codes.append(str(code))
            return codes
        except Exception as e:
            logger.error(f"查询没有报告日期 {report_date} 的股票代码失败: {e}", exc_info=True)
            return []

