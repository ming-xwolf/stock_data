"""
涨跌停查询服务模块

提供股票涨跌停数据的查询功能。
根据上海、深圳、北交所的不同规则计算涨跌停。
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP

from .db import db_manager

logger = logging.getLogger(__name__)


class LimitService:
    """涨跌停查询服务类"""
    
    # 涨跌幅限制规则
    # 上海主板(60开头): 10%
    # 深圳主板(00开头): 10%
    # 深圳创业板(30开头): 20%
    # 上海科创板(68开头): 20%
    # 北交所(8开头,92开头): 30%
    LIMIT_RULES = {
        'SH_MAIN': 0.10,      # 上海主板: 10%
        'SZ_MAIN': 0.10,      # 深圳主板: 10%
        'SZ_CHUANGYE': 0.20,  # 深圳创业板: 20%
        'SH_KEJI': 0.20,      # 上海科创板: 20%
        'BJ': 0.30,           # 北交所: 30%
    }
    
    # 查询涨跌停股票的SQL（优化版：使用自连接提高性能，避免窗口函数在大数据量时的性能问题）
    SELECT_LIMIT_STOCKS_SQL = """
        SELECT 
            d.code,
            s.name,
            s.market,
            d.trade_date,
            d.open_price,
            d.high_price,
            d.low_price,
            d.close_price,
            d.volume,
            d.amount,
            d.turnover,
            prev.close_price as prev_close_price,
            CASE 
                WHEN d.code LIKE '60%%' THEN 0.10
                WHEN d.code LIKE '68%%' THEN 0.20
                WHEN d.code LIKE '00%%' THEN 0.10
                WHEN d.code LIKE '30%%' THEN 0.20
                WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                ELSE 0.10
            END as limit_ratio,
            CASE 
                WHEN d.close_price >= prev.close_price * (1 + 
                    CASE 
                        WHEN d.code LIKE '60%%' THEN 0.10
                        WHEN d.code LIKE '68%%' THEN 0.20
                        WHEN d.code LIKE '00%%' THEN 0.10
                        WHEN d.code LIKE '30%%' THEN 0.20
                        WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                        ELSE 0.10
                    END
                ) - 0.01 THEN '涨停'
                WHEN d.close_price <= prev.close_price * (1 - 
                    CASE 
                        WHEN d.code LIKE '60%%' THEN 0.10
                        WHEN d.code LIKE '68%%' THEN 0.20
                        WHEN d.code LIKE '00%%' THEN 0.10
                        WHEN d.code LIKE '30%%' THEN 0.20
                        WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                        ELSE 0.10
                    END
                ) + 0.01 THEN '跌停'
                ELSE '正常'
            END as limit_status,
            ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
        FROM stock_daily d
        INNER JOIN stocks s ON d.code = s.code
        INNER JOIN stock_daily prev ON d.code = prev.code 
            AND prev.trade_date = (
                SELECT MAX(trade_date) 
                FROM stock_daily 
                WHERE code = d.code 
                AND trade_date < d.trade_date
            )
        WHERE d.trade_date >= %s
        AND d.trade_date <= %s
        AND prev.close_price IS NOT NULL
        AND prev.close_price > 0
        HAVING limit_status IN ('涨停', '跌停')
        ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
    """
    
    # 查询指定股票的涨跌停记录（优化版：使用自连接，对单只股票性能更好）
    SELECT_STOCK_LIMIT_SQL = """
        SELECT 
            d.code,
            s.name,
            s.market,
            d.trade_date,
            d.open_price,
            d.high_price,
            d.low_price,
            d.close_price,
            d.volume,
            d.amount,
            d.turnover,
            prev.close_price as prev_close_price,
            CASE 
                WHEN d.code LIKE '60%%' THEN 0.10
                WHEN d.code LIKE '68%%' THEN 0.20
                WHEN d.code LIKE '00%%' THEN 0.10
                WHEN d.code LIKE '30%%' THEN 0.20
                WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                ELSE 0.10
            END as limit_ratio,
            CASE 
                WHEN d.close_price >= prev.close_price * (1 + 
                    CASE 
                        WHEN d.code LIKE '60%%' THEN 0.10
                        WHEN d.code LIKE '68%%' THEN 0.20
                        WHEN d.code LIKE '00%%' THEN 0.10
                        WHEN d.code LIKE '30%%' THEN 0.20
                        WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                        ELSE 0.10
                    END
                ) - 0.01 THEN '涨停'
                WHEN d.close_price <= prev.close_price * (1 - 
                    CASE 
                        WHEN d.code LIKE '60%%' THEN 0.10
                        WHEN d.code LIKE '68%%' THEN 0.20
                        WHEN d.code LIKE '00%%' THEN 0.10
                        WHEN d.code LIKE '30%%' THEN 0.20
                        WHEN d.code LIKE '8%%' OR d.code LIKE '92%%' THEN 0.30
                        ELSE 0.10
                    END
                ) + 0.01 THEN '跌停'
                ELSE '正常'
            END as limit_status,
            ROUND((d.close_price - prev.close_price) / prev.close_price * 100, 2) as change_pct
        FROM stock_daily d
        INNER JOIN stocks s ON d.code = s.code
        INNER JOIN stock_daily prev ON d.code = prev.code 
            AND prev.trade_date = (
                SELECT MAX(trade_date) 
                FROM stock_daily 
                WHERE code = d.code 
                AND trade_date < d.trade_date
            )
        WHERE d.code = %s
        AND d.trade_date >= %s
        AND d.trade_date <= %s
        AND prev.close_price IS NOT NULL
        AND prev.close_price > 0
        HAVING limit_status IN ('涨停', '跌停')
        ORDER BY d.trade_date DESC, limit_status ASC, change_pct DESC
    """
    
    @staticmethod
    def get_limit_ratio(code: str) -> float:
        """
        根据股票代码获取涨跌幅限制比例
        
        Args:
            code: 股票代码
            
        Returns:
            涨跌幅限制比例（如0.10表示10%）
        """
        if code.startswith('60'):
            # 上海主板: 10%
            return LimitService.LIMIT_RULES['SH_MAIN']
        elif code.startswith('68'):
            # 上海科创板: 20%
            return LimitService.LIMIT_RULES['SH_KEJI']
        elif code.startswith('00'):
            # 深圳主板: 10%
            return LimitService.LIMIT_RULES['SZ_MAIN']
        elif code.startswith('30'):
            # 深圳创业板: 20%
            return LimitService.LIMIT_RULES['SZ_CHUANGYE']
        elif code.startswith(('8', '92')):
            # 北交所: 30%
            return LimitService.LIMIT_RULES['BJ']
        else:
            # 默认10%
            logger.warning(f"无法识别股票代码 {code} 的交易所，使用默认10%涨跌幅限制")
            return LimitService.LIMIT_RULES['SH_MAIN']
    
    @staticmethod
    def calculate_limit_price(prev_close: float, limit_ratio: float, is_up: bool = True) -> float:
        """
        计算涨跌停价格
        
        Args:
            prev_close: 前一日收盘价
            limit_ratio: 涨跌幅限制比例
            is_up: True表示涨停，False表示跌停
            
        Returns:
            涨跌停价格（保留2位小数）
        """
        if is_up:
            # 涨停: 前收盘价 * (1 + 涨跌幅限制)
            limit_price = prev_close * (1 + limit_ratio)
        else:
            # 跌停: 前收盘价 * (1 - 涨跌幅限制)
            limit_price = prev_close * (1 - limit_ratio)
        
        # 保留2位小数，四舍五入
        return float(Decimal(str(limit_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @staticmethod
    def is_limit_up(close_price: float, prev_close: float, limit_ratio: float) -> bool:
        """
        判断是否涨停
        
        Args:
            close_price: 当日收盘价
            prev_close: 前一日收盘价
            limit_ratio: 涨跌幅限制比例
            
        Returns:
            是否涨停
        """
        if prev_close <= 0:
            return False
        
        limit_up_price = LimitService.calculate_limit_price(prev_close, limit_ratio, is_up=True)
        # 考虑浮点数精度，允许0.01的误差
        return close_price >= limit_up_price - 0.01
    
    @staticmethod
    def is_limit_down(close_price: float, prev_close: float, limit_ratio: float) -> bool:
        """
        判断是否跌停
        
        Args:
            close_price: 当日收盘价
            prev_close: 前一日收盘价
            limit_ratio: 涨跌幅限制比例
            
        Returns:
            是否跌停
        """
        if prev_close <= 0:
            return False
        
        limit_down_price = LimitService.calculate_limit_price(prev_close, limit_ratio, is_up=False)
        # 考虑浮点数精度，允许0.01的误差
        return close_price <= limit_down_price + 0.01
    
    def query_limit_stocks(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        limit_type: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        查询指定日期范围内的涨跌停股票
        
        Args:
            start_date: 起始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式），如果为None则使用今天
            limit_type: 限制类型，'涨停'或'跌停'，如果为None则查询所有涨跌停
            
        Returns:
            涨跌停股票列表，每个元素包含：
            - code: 股票代码
            - name: 股票名称
            - market: 市场代码
            - trade_date: 交易日期
            - open_price: 开盘价
            - high_price: 最高价
            - low_price: 最低价
            - close_price: 收盘价
            - volume: 成交量
            - amount: 成交额
            - turnover: 换手率
            - prev_close_price: 前一日收盘价
            - limit_status: 涨跌停状态（'涨停'或'跌停'）
            - change_pct: 涨跌幅（%）
        """
        try:
            # 如果没有指定结束日期，使用今天
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 验证日期格式
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"日期格式错误: {e}")
                return []
            
            # 使用优化的SQL查询，一次性获取所有涨跌停记录
            # 注意：使用自连接方式，只需要2个参数：start_date和end_date
            results = db_manager.execute_query(
                self.SELECT_LIMIT_STOCKS_SQL,
                (start_date, end_date)
            )
            
            # 过滤涨跌停类型
            if limit_type:
                results = [r for r in results if r.get('limit_status') == limit_type]
            
            logger.info(f"查询到 {len(results)} 条涨跌停记录（日期范围: {start_date} 到 {end_date}）")
            return results
            
        except Exception as e:
            logger.error(f"查询涨跌停股票失败: {e}", exc_info=True)
            return []
    
    def query_stock_limit_history(
        self,
        code: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        查询指定股票的历史涨跌停记录
        
        Args:
            code: 股票代码
            start_date: 起始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式），如果为None则使用今天
            
        Returns:
            涨跌停记录列表
        """
        try:
            # 如果没有指定结束日期，使用今天
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 查询涨跌停记录（SQL中已包含涨跌幅限制计算）
            # 注意：使用自连接方式，只需要3个参数：code、start_date和end_date
            results = db_manager.execute_query(
                self.SELECT_STOCK_LIMIT_SQL,
                (code, start_date, end_date)
            )
            
            logger.info(f"股票 {code} 在 {start_date} 到 {end_date} 期间有 {len(results)} 次涨跌停")
            return results
            
        except Exception as e:
            logger.error(f"查询股票 {code} 涨跌停历史失败: {e}", exc_info=True)
            return []
    
    def get_limit_statistics(
        self,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, any]:
        """
        获取涨跌停统计信息
        
        Args:
            start_date: 起始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式），如果为None则使用今天
            
        Returns:
            统计信息字典，包含：
            - total_limit_up: 涨停总数
            - total_limit_down: 跌停总数
            - limit_up_by_date: 按日期统计的涨停数
            - limit_down_by_date: 按日期统计的跌停数
        """
        try:
            # 查询所有涨跌停记录
            all_records = self.query_limit_stocks(start_date, end_date)
            
            # 统计
            total_limit_up = sum(1 for r in all_records if r.get('limit_status') == '涨停')
            total_limit_down = sum(1 for r in all_records if r.get('limit_status') == '跌停')
            
            # 按日期统计
            limit_up_by_date = {}
            limit_down_by_date = {}
            
            for record in all_records:
                trade_date = record.get('trade_date')
                if isinstance(trade_date, datetime):
                    trade_date = trade_date.strftime('%Y-%m-%d')
                elif not isinstance(trade_date, str):
                    trade_date = str(trade_date)
                
                limit_status = record.get('limit_status')
                if limit_status == '涨停':
                    limit_up_by_date[trade_date] = limit_up_by_date.get(trade_date, 0) + 1
                elif limit_status == '跌停':
                    limit_down_by_date[trade_date] = limit_down_by_date.get(trade_date, 0) + 1
            
            return {
                'total_limit_up': total_limit_up,
                'total_limit_down': total_limit_down,
                'limit_up_by_date': limit_up_by_date,
                'limit_down_by_date': limit_down_by_date,
                'total_records': len(all_records)
            }
            
        except Exception as e:
            logger.error(f"获取涨跌停统计信息失败: {e}", exc_info=True)
            return {
                'total_limit_up': 0,
                'total_limit_down': 0,
                'limit_up_by_date': {},
                'limit_down_by_date': {},
                'total_records': 0
            }
