"""
ETF 日线行情数据服务模块

提供 ETF 日线行情数据的存储和查询功能。
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..core.db import db_manager
from .sql_queries import sql_manager
from .sql_queries import etf_daily_sql

logger = logging.getLogger(__name__)


class ETFDailyService:
    """ETF 日线行情数据服务类"""
    
    def __init__(self):
        """初始化服务，加载 SQL 语句"""
        self.INSERT_DAILY_SQL = sql_manager.get_sql(etf_daily_sql, 'INSERT_DAILY')
        self.SELECT_LATEST_DATE_SQL = sql_manager.get_sql(etf_daily_sql, 'SELECT_LATEST_DATE')
        self.SELECT_DAILY_DATA_SQL = sql_manager.get_sql(etf_daily_sql, 'SELECT_DAILY_DATA')
        self.COUNT_DAILY_SQL = sql_manager.get_sql(etf_daily_sql, 'COUNT_DAILY')
        self.SELECT_EXISTING_DATES_SQL = sql_manager.get_sql(etf_daily_sql, 'SELECT_EXISTING_DATES')
        self.SELECT_ETFS_NEED_UPDATE_SQL = sql_manager.get_sql(etf_daily_sql, 'SELECT_ETFS_NEED_UPDATE')
    
    def insert_daily_data(self, data: Dict[str, any]) -> bool:
        """
        插入或更新单条日线数据
        
        Args:
            data: 日线数据字典
            
        Returns:
            是否成功
        """
        try:
            affected_rows = db_manager.execute_update(
                self.INSERT_DAILY_SQL,
                (
                    data['code'],
                    data['trade_date'],
                    data.get('open_price'),
                    data.get('high_price'),
                    data.get('low_price'),
                    data.get('close_price'),
                    data.get('volume'),
                    data.get('amount'),
                    data.get('change_amount'),
                    data.get('change_rate'),
                    data.get('turnover')
                )
            )
            logger.debug(f"插入/更新 ETF {data['code']} 日线数据 {data['trade_date']}: {affected_rows} 行受影响")
            return True
        except Exception as e:
            logger.error(f"插入日线数据失败: {e}")
            return False
    
    def batch_insert_daily_data(self, data_list: List[Dict[str, any]]) -> int:
        """
        批量插入或更新日线数据
        
        Args:
            data_list: 日线数据列表
            
        Returns:
            成功插入/更新的数据条数
        """
        if not data_list:
            return 0
        
        try:
            params_list = [
                (
                    data['code'],
                    data['trade_date'],
                    data.get('open_price'),
                    data.get('high_price'),
                    data.get('low_price'),
                    data.get('close_price'),
                    data.get('volume'),
                    data.get('amount'),
                    data.get('change_amount'),
                    data.get('change_rate'),
                    data.get('turnover')
                )
                for data in data_list
            ]
            
            affected_rows = db_manager.execute_many(
                self.INSERT_DAILY_SQL,
                params_list
            )
            
            logger.info(f"批量插入/更新日线数据: {affected_rows} 行受影响")
            return affected_rows
            
        except Exception as e:
            # 如果批量插入失败，尝试逐条插入以定位问题
            error_msg = str(e)
            if 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
                logger.warning(f"批量插入遇到冲突，尝试逐条插入以定位问题: {error_msg}")
                return self._insert_one_by_one(data_list)
            else:
                logger.error(f"批量插入日线数据失败: {e}", exc_info=True)
                raise
    
    def _insert_one_by_one(self, data_list: List[Dict[str, any]]) -> int:
        """
        逐条插入数据（用于调试和错误恢复）
        
        Args:
            data_list: 日线数据列表
            
        Returns:
            成功插入/更新的数据条数
        """
        success_count = 0
        failed_count = 0
        
        for i, data in enumerate(data_list):
            try:
                self.insert_daily_data(data)
                success_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"插入第 {i+1} 条数据失败 (code={data.get('code')}, date={data.get('trade_date')}): {e}")
        
        if failed_count > 0:
            logger.warning(f"逐条插入完成: 成功 {success_count} 条，失败 {failed_count} 条")
        else:
            logger.info(f"逐条插入完成: 成功 {success_count} 条")
        
        return success_count
    
    def get_latest_date(self, code: str) -> Optional[str]:
        """
        获取指定 ETF 的最新交易日期
        
        Args:
            code: ETF 代码
            
        Returns:
            最新交易日期（YYYY-MM-DD格式），如果没有数据返回 None
        """
        try:
            results = db_manager.execute_query(self.SELECT_LATEST_DATE_SQL, (code,))
            if results and results[0]['latest_date']:
                latest_date = results[0]['latest_date']
                # 转换为字符串格式
                if isinstance(latest_date, datetime):
                    return latest_date.strftime('%Y-%m-%d')
                return str(latest_date)
            return None
        except Exception as e:
            logger.error(f"查询 ETF {code} 最新日期失败: {e}")
            return None
    
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> List[Dict[str, any]]:
        """
        查询指定日期范围的日线数据
        
        Args:
            code: ETF 代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            日线数据列表
        """
        try:
            return db_manager.execute_query(
                self.SELECT_DAILY_DATA_SQL,
                (code, start_date, end_date)
            )
        except Exception as e:
            logger.error(f"查询 ETF {code} 日线数据失败: {e}")
            return []
    
    def count_daily_records(self, code: str) -> int:
        """
        统计指定 ETF 的日线数据条数
        
        Args:
            code: ETF 代码
            
        Returns:
            数据条数
        """
        try:
            results = db_manager.execute_query(self.COUNT_DAILY_SQL, (code,))
            if results:
                return results[0]['count']
            return 0
        except Exception as e:
            logger.error(f"统计 ETF {code} 日线数据失败: {e}")
            return 0
    
    def get_existing_dates(self, code: str, start_date: str, end_date: str) -> set:
        """
        获取指定 ETF 在指定日期范围内已存在的交易日期
        
        Args:
            code: ETF 代码
            start_date: 开始日期（YYYY-MM-DD格式）
            end_date: 结束日期（YYYY-MM-DD格式）
            
        Returns:
            已存在的日期集合（字符串格式：YYYY-MM-DD）
        """
        try:
            results = db_manager.execute_query(
                self.SELECT_EXISTING_DATES_SQL,
                (code, start_date, end_date)
            )
            existing_dates = set()
            for row in results:
                trade_date = row['trade_date']
                # 转换为字符串格式
                if isinstance(trade_date, datetime):
                    existing_dates.add(trade_date.strftime('%Y-%m-%d'))
                else:
                    existing_dates.add(str(trade_date))
            return existing_dates
        except Exception as e:
            logger.error(f"查询 ETF {code} 已存在日期失败: {e}")
            return set()
    
    def batch_insert_daily_data_filtered(self, data_list: List[Dict[str, any]], 
                                         check_existing: bool = True) -> int:
        """
        批量插入或更新日线数据（自动过滤已存在的数据）
        
        Args:
            data_list: 日线数据列表
            check_existing: 是否检查已存在的数据（默认True）
            
        Returns:
            成功插入/更新的数据条数
        """
        if not data_list:
            return 0
        
        # 第一步：去除数据列表中的重复项（基于 code 和 trade_date）
        seen = set()
        unique_data_list = []
        for data in data_list:
            # 统一日期格式为字符串（YYYY-MM-DD）
            trade_date = data['trade_date']
            if isinstance(trade_date, datetime):
                trade_date_str = trade_date.strftime('%Y-%m-%d')
            else:
                trade_date_str = str(trade_date)
            
            # 创建唯一标识
            key = (data['code'], trade_date_str)
            if key not in seen:
                seen.add(key)
                # 确保 trade_date 是字符串格式
                data_copy = data.copy()
                data_copy['trade_date'] = trade_date_str
                unique_data_list.append(data_copy)
        
        if len(unique_data_list) < len(data_list):
            logger.info(f"去除了 {len(data_list) - len(unique_data_list)} 条重复数据")
        
        data_list = unique_data_list
        
        # 如果启用检查，先过滤掉已存在的数据
        if check_existing and data_list:
            # 获取第一只ETF的代码（假设列表中所有数据的code相同）
            code = data_list[0]['code']
            
            # 找到日期范围（确保是字符串格式）
            dates = [data['trade_date'] for data in data_list]
            start_date = min(dates)
            end_date = max(dates)
            
            # 查询已存在的日期
            existing_dates = self.get_existing_dates(code, start_date, end_date)
            
            if existing_dates:
                logger.info(f"ETF {code} 在 {start_date} 到 {end_date} 范围内已有 {len(existing_dates)} 个日期，将过滤这些日期")
                # 过滤掉已存在的数据
                original_count = len(data_list)
                data_list = [
                    data for data in data_list 
                    if data['trade_date'] not in existing_dates
                ]
                filtered_count = original_count - len(data_list)
                if filtered_count > 0:
                    logger.info(f"已过滤 {filtered_count} 条已存在的数据，剩余 {len(data_list)} 条新数据")
            
            # 如果没有新数据，直接返回
            if not data_list:
                logger.info(f"ETF {code} 所有数据已存在，无需插入")
                return 0
        
        # 调用原有的批量插入方法
        return self.batch_insert_daily_data(data_list)
    
    def get_etfs_need_update(self) -> List[Dict[str, any]]:
        """
        获取需要更新的 ETF 列表（缺少最新交易日数据的 ETF）
        
        该方法会：
        1. 查询交易日历的最新交易日
        2. 结合 etf_funds 表，找出 etf_daily 中缺少最新交易日数据的 ETF
        3. 返回需要更新的 ETF 列表，包含建议的起始日期
        
        Returns:
            需要更新的 ETF 列表，每个元素包含：
            - code: ETF 代码
            - name: ETF 名称
            - latest_daily_date: 该 ETF 在数据库中的最新日期
            - latest_trading_date: 交易日历中的最新交易日
            - start_date: 建议的更新起始日期（从该 ETF 最新日期的下一天开始）
        """
        try:
            results = db_manager.execute_query(self.SELECT_ETFS_NEED_UPDATE_SQL)
            
            # 转换日期格式
            etfs_need_update = []
            for row in results:
                etf_info = {
                    'code': row['code'],
                    'name': row.get('name', ''),
                    'latest_daily_date': None,
                    'latest_trading_date': None,
                    'start_date': None
                }
                
                # 转换 latest_daily_date
                if row.get('latest_daily_date'):
                    latest_daily = row['latest_daily_date']
                    if isinstance(latest_daily, datetime):
                        etf_info['latest_daily_date'] = latest_daily.strftime('%Y-%m-%d')
                    else:
                        etf_info['latest_daily_date'] = str(latest_daily)
                
                # 转换 latest_trading_date
                if row.get('latest_trading_date'):
                    latest_trading = row['latest_trading_date']
                    if isinstance(latest_trading, datetime):
                        etf_info['latest_trading_date'] = latest_trading.strftime('%Y-%m-%d')
                    else:
                        etf_info['latest_trading_date'] = str(latest_trading)
                
                # 转换 start_date
                if row.get('start_date'):
                    start = row['start_date']
                    if isinstance(start, datetime):
                        etf_info['start_date'] = start.strftime('%Y-%m-%d')
                    else:
                        etf_info['start_date'] = str(start)
                
                etfs_need_update.append(etf_info)
            
            return etfs_need_update
            
        except Exception as e:
            logger.error(f"查询需要更新的 ETF 列表失败: {e}", exc_info=True)
            return []
