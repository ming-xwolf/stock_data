"""
技术指标选股条件实现

提供价格、成交量、涨跌幅、技术指标等筛选条件。
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

from .base import BaseCondition

logger = logging.getLogger(__name__)


class PriceCondition(BaseCondition):
    """价格筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选价格范围内的股票
        
        参数：
            min_price: 最低价格
            max_price: 最高价格
            date: 查询日期（YYYY-MM-DD格式），默认最新交易日
        """
        min_price = self.params.get('min_price')
        max_price = self.params.get('max_price')
        date = self.params.get('date')
        
        if not stock_codes:
            return []
        
        if min_price is None and max_price is None:
            return stock_codes
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_data_service
        
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        # 如果没有指定日期，使用最新交易日
        if not date:
            date = fetch_service.get_latest_trade_date()
            if not date:
                logger.warning("无法获取最新交易日")
                return []
        
        result_codes = []
        
        try:
            # 批量查询指定日期的价格数据
            sql = """
                SELECT code, close_price
                FROM stock_daily
                WHERE code = ANY(%s)
                AND trade_date = %s
            """
            results = db_manager.execute_query(sql, (stock_codes, date))
            
            for row in results:
                price = row['close_price']
                if price is None:
                    continue
                
                # 判断是否符合条件
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
                
                result_codes.append(row['code'])
        except Exception as e:
            logger.error(f"价格筛选失败: {e}")
            return []
        
        return result_codes


class VolumeCondition(BaseCondition):
    """成交量筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选成交量范围内的股票
        
        参数：
            min_volume: 最小成交量
            max_volume: 最大成交量
            date: 查询日期（YYYY-MM-DD格式），默认最新交易日
        """
        min_volume = self.params.get('min_volume')
        max_volume = self.params.get('max_volume')
        date = self.params.get('date')
        
        if not stock_codes:
            return []
        
        if min_volume is None and max_volume is None:
            return stock_codes
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_data_service
        
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        # 如果没有指定日期，使用最新交易日
        if not date:
            date = fetch_service.get_latest_trade_date()
            if not date:
                logger.warning("无法获取最新交易日")
                return []
        
        result_codes = []
        
        try:
            # 批量查询指定日期的成交量数据
            sql = """
                SELECT code, volume
                FROM stock_daily
                WHERE code = ANY(%s)
                AND trade_date = %s
            """
            results = db_manager.execute_query(sql, (stock_codes, date))
            
            for row in results:
                volume = row['volume']
                if volume is None:
                    continue
                
                # 判断是否符合条件
                if min_volume is not None and volume < min_volume:
                    continue
                if max_volume is not None and volume > max_volume:
                    continue
                
                result_codes.append(row['code'])
        except Exception as e:
            logger.error(f"成交量筛选失败: {e}")
            return []
        
        return result_codes


class ChangeRateCondition(BaseCondition):
    """涨跌幅筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选涨跌幅范围内的股票
        
        参数：
            days: 计算天数（默认5）
            min_rate: 最小涨跌幅（如0.1表示10%）
            max_rate: 最大涨跌幅
            date: 结束日期（YYYY-MM-DD格式），默认最新交易日
        """
        days = self.params.get('days', 5)
        min_rate = self.params.get('min_rate')
        max_rate = self.params.get('max_rate')
        date = self.params.get('date')
        
        if not stock_codes:
            return []
        
        if min_rate is None and max_rate is None:
            return stock_codes
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_service
        
        # 如果没有指定日期，使用最新交易日
        if not date:
            date = fetch_service.get_latest_trade_date()
            if not date:
                logger.warning("无法获取最新交易日")
                return []
        
        # 计算开始日期
        end_date_obj = datetime.strptime(date, '%Y-%m-%d')
        start_date_obj = end_date_obj - timedelta(days=days * 2)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        
        result_codes = []
        
        for code in stock_codes:
            try:
                # 获取股票数据
                df = fetch_service.fetch_stock_data(code, start_date, date)
                
                if len(df) < days:
                    continue
                
                # 计算涨跌幅
                start_price = df.iloc[-days]['close']
                end_price = df.iloc[-1]['close']
                change_rate = (end_price - start_price) / start_price
                
                # 判断是否符合条件
                if min_rate is not None and change_rate < min_rate:
                    continue
                if max_rate is not None and change_rate > max_rate:
                    continue
                
                result_codes.append(code)
                
            except Exception as e:
                logger.debug(f"计算股票 {code} 涨跌幅失败: {e}")
                continue
        
        return result_codes


class TurnoverCondition(BaseCondition):
    """换手率筛选条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选换手率范围内的股票
        
        参数：
            min_turnover: 最小换手率（%）
            max_turnover: 最大换手率（%）
            date: 查询日期（YYYY-MM-DD格式），默认最新交易日
        """
        min_turnover = self.params.get('min_turnover')
        max_turnover = self.params.get('max_turnover')
        date = self.params.get('date')
        
        if not stock_codes:
            return []
        
        if min_turnover is None and max_turnover is None:
            return stock_codes
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_data_service
        
        if context and 'db_manager' in context:
            db_manager = context['db_manager']
        else:
            from ...core.db import db_manager
        
        # 如果没有指定日期，使用最新交易日
        if not date:
            date = fetch_service.get_latest_trade_date()
            if not date:
                logger.warning("无法获取最新交易日")
                return []
        
        result_codes = []
        
        try:
            # 批量查询指定日期的换手率数据
            sql = """
                SELECT code, turnover
                FROM stock_daily
                WHERE code = ANY(%s)
                AND trade_date = %s
            """
            results = db_manager.execute_query(sql, (stock_codes, date))
            
            for row in results:
                turnover = row['turnover']
                if turnover is None:
                    continue
                
                # 判断是否符合条件
                if min_turnover is not None and turnover < min_turnover:
                    continue
                if max_turnover is not None and turnover > max_turnover:
                    continue
                
                result_codes.append(row['code'])
        except Exception as e:
            logger.error(f"换手率筛选失败: {e}")
            return []
        
        return result_codes


class MACDCondition(BaseCondition):
    """MACD指标条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选MACD条件
        
        参数：
            signal: 'golden_cross' (金叉) 或 'death_cross' (死叉) 或 'positive' (MACD>0) 或 'negative' (MACD<0)
            period: 'D' (日线), 'W' (周线), 'M' (月线)
            days: 计算周期（默认60）
        """
        signal = self.params.get('signal', 'golden_cross')
        period = self.params.get('period', 'D')
        days = self.params.get('days', 60)
        
        if not stock_codes:
            return []
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_service
        
        from ...charts.indicators import calculate_indicators
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        result_codes = []
        
        for code in stock_codes:
            try:
                # 获取股票数据
                df = fetch_service.fetch_stock_data(code, start_date, end_date)
                
                if len(df) < 30:  # 数据不足
                    continue
                
                # 计算MACD
                df = calculate_indicators(df, period)
                
                # 检查是否有NaN值
                if df['DIF'].isna().any() or df['DEA'].isna().any():
                    continue
                
                # 检查最新数据
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                
                # 判断金叉或死叉
                if signal == 'golden_cross':
                    # 金叉：DIF上穿DEA
                    if prev['DIF'] <= prev['DEA'] and latest['DIF'] > latest['DEA']:
                        result_codes.append(code)
                elif signal == 'death_cross':
                    # 死叉：DIF下穿DEA
                    if prev['DIF'] >= prev['DEA'] and latest['DIF'] < latest['DEA']:
                        result_codes.append(code)
                elif signal == 'positive':
                    # MACD柱状图为正
                    if latest['MACD'] > 0:
                        result_codes.append(code)
                elif signal == 'negative':
                    # MACD柱状图为负
                    if latest['MACD'] < 0:
                        result_codes.append(code)
                        
            except Exception as e:
                logger.debug(f"计算股票 {code} MACD失败: {e}")
                continue
        
        return result_codes


class BOLLCondition(BaseCondition):
    """布林带条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选布林带条件
        
        参数：
            signal: 
                - 'upper' (价格触及上轨)
                - 'lower' (价格触及下轨)
                - 'middle' (价格在中轨附近)
                - 'top_divergence' (顶背离：价格创新高但BOLL中轨未创新高)
                - 'bottom_divergence' (底背离：价格创新低但BOLL中轨未创新低)
            period: 'D' (日线), 'W' (周线), 'M' (月线)
            days: 计算周期（默认60）
            lookback_days: 背离检测的回看天数（默认20）
        """
        signal = self.params.get('signal', 'upper')
        period = self.params.get('period', 'D')
        days = self.params.get('days', 60)
        lookback_days = self.params.get('lookback_days', 20)
        
        if not stock_codes:
            return []
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_data_service
        
        from ...charts.indicators import calculate_indicators
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        result_codes = []
        
        for code in stock_codes:
            try:
                # 获取股票数据
                df = fetch_service.fetch_stock_data(code, start_date, end_date)
                
                if len(df) < 20:  # 数据不足
                    continue
                
                # 计算BOLL
                df = calculate_indicators(df, period)
                
                # 检查是否有NaN值
                if df['BOLL_UPPER'].isna().any() or df['BOLL_LOWER'].isna().any():
                    continue
                
                # 检查最新数据
                latest = df.iloc[-1]
                price = latest['close']
                upper = latest['BOLL_UPPER']
                lower = latest['BOLL_LOWER']
                middle = latest['BOLL_MIDDLE']
                
                # 判断条件
                if signal == 'upper':
                    # 价格触及或突破上轨
                    if price >= upper * 0.99:  # 允许1%的误差
                        result_codes.append(code)
                elif signal == 'lower':
                    # 价格触及或跌破下轨
                    if price <= lower * 1.01:  # 允许1%的误差
                        result_codes.append(code)
                elif signal == 'middle':
                    # 价格在中轨附近（±2%）
                    if abs(price - middle) / middle <= 0.02:
                        result_codes.append(code)
                elif signal == 'top_divergence':
                    # 顶背离：价格创新高但BOLL中轨未创新高
                    if len(df) < lookback_days:
                        continue
                    
                    # 获取最近lookback_days天的数据
                    recent_df = df.iloc[-lookback_days:]
                    
                    # 找到价格最高点和对应的中轨值
                    price_max_idx = recent_df['close'].idxmax()
                    price_max = recent_df.loc[price_max_idx, 'close']
                    middle_at_price_max = recent_df.loc[price_max_idx, 'BOLL_MIDDLE']
                    
                    # 当前价格和中轨值
                    current_price = latest['close']
                    current_middle = latest['BOLL_MIDDLE']
                    
                    # 判断是否顶背离：
                    # 1. 当前价格是最近的高点（或接近高点）
                    # 2. 但当前中轨值低于或等于价格最高时的中轨值
                    # 3. 价格创新高但中轨未创新高
                    if (current_price >= price_max * 0.95 and  # 当前价格接近或超过最高点
                        current_middle <= middle_at_price_max * 1.01):  # 中轨未创新高（允许1%误差）
                        result_codes.append(code)
                elif signal == 'bottom_divergence':
                    # 底背离：价格创新低但BOLL中轨未创新低
                    if len(df) < lookback_days:
                        continue
                    
                    # 获取最近lookback_days天的数据
                    recent_df = df.iloc[-lookback_days:]
                    
                    # 找到价格最低点和对应的中轨值
                    price_min_idx = recent_df['close'].idxmin()
                    price_min = recent_df.loc[price_min_idx, 'close']
                    middle_at_price_min = recent_df.loc[price_min_idx, 'BOLL_MIDDLE']
                    
                    # 当前价格和中轨值
                    current_price = latest['close']
                    current_middle = latest['BOLL_MIDDLE']
                    
                    # 判断是否底背离：
                    # 1. 当前价格是最近的低点（或接近低点）
                    # 2. 但当前中轨值高于或等于价格最低时的中轨值
                    # 3. 价格创新低但中轨未创新低
                    if (current_price <= price_min * 1.05 and  # 当前价格接近或低于最低点
                        current_middle >= middle_at_price_min * 0.99):  # 中轨未创新低（允许1%误差）
                        result_codes.append(code)
                        
            except Exception as e:
                logger.debug(f"计算股票 {code} BOLL失败: {e}")
                continue
        
        return result_codes


class MovingAverageCondition(BaseCondition):
    """均线条件"""
    
    def filter(
        self, 
        stock_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        筛选均线条件
        
        参数：
            signal: 'above' (价格在均线上方) 或 'below' (价格在均线下方) 或 'cross_up' (价格上穿均线) 或 'cross_down' (价格下穿均线)
            period: 均线周期（如5、10、20、30、60等）
            days: 计算周期（默认60）
        """
        signal = self.params.get('signal', 'above')
        period = self.params.get('period', 20)
        days = self.params.get('days', 60)
        
        if not stock_codes:
            return []
        
        # 从上下文获取服务
        if context and 'fetch_service' in context:
            fetch_service = context['fetch_service']
        else:
            from ...services.fetch_data_service import fetch_data_service
            fetch_service = fetch_service
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')
        
        result_codes = []
        
        for code in stock_codes:
            try:
                # 获取股票数据
                df = fetch_service.fetch_stock_data(code, start_date, end_date)
                
                if len(df) < period:
                    continue
                
                # 计算均线
                df['MA'] = df['close'].rolling(window=period).mean()
                
                # 检查是否有NaN值
                if df['MA'].isna().any():
                    continue
                
                # 检查最新数据
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                
                price = latest['close']
                ma = latest['MA']
                prev_price = prev['close']
                prev_ma = prev['MA']
                
                # 判断条件
                if signal == 'above':
                    # 价格在均线上方
                    if price > ma:
                        result_codes.append(code)
                elif signal == 'below':
                    # 价格在均线下方
                    if price < ma:
                        result_codes.append(code)
                elif signal == 'cross_up':
                    # 价格上穿均线
                    if prev_price <= prev_ma and price > ma:
                        result_codes.append(code)
                elif signal == 'cross_down':
                    # 价格下穿均线
                    if prev_price >= prev_ma and price < ma:
                        result_codes.append(code)
                        
            except Exception as e:
                logger.debug(f"计算股票 {code} 均线失败: {e}")
                continue
        
        return result_codes
