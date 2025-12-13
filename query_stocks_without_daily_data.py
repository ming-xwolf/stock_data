#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询没有历史行情的股票统计信息
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db import db_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 统计SQL
COUNT_STOCKS_WITHOUT_DAILY_SQL = """
    SELECT COUNT(*) as count
    FROM stocks s
    WHERE NOT EXISTS (
        SELECT 1 
        FROM stock_daily sd 
        WHERE sd.code = s.code
    )
"""

# 按市场统计SQL
COUNT_BY_MARKET_SQL = """
    SELECT 
        s.market,
        COUNT(*) as count
    FROM stocks s
    WHERE NOT EXISTS (
        SELECT 1 
        FROM stock_daily sd 
        WHERE sd.code = s.code
    )
    GROUP BY s.market
    ORDER BY s.market
"""

# 按企业性质统计SQL
COUNT_BY_COMPANY_TYPE_SQL = """
    SELECT 
        COALESCE(s.company_type, '未知') as company_type,
        COUNT(*) as count
    FROM stocks s
    WHERE NOT EXISTS (
        SELECT 1 
        FROM stock_daily sd 
        WHERE sd.code = s.code
    )
    GROUP BY s.company_type
    ORDER BY count DESC
"""


def query_stocks_without_daily_data():
    """查询没有历史行情的股票统计信息"""
    
    logger.info("=" * 80)
    logger.info("没有历史行情的股票统计信息")
    logger.info("=" * 80)
    
    try:
        # 1. 统计总数
        logger.info("\n正在统计...")
        count_result = db_manager.execute_query(COUNT_STOCKS_WITHOUT_DAILY_SQL)
        total_count = count_result[0]['count'] if count_result else 0
        
        logger.info(f"\n总计: {total_count} 只股票没有历史行情数据")
        
        if total_count == 0:
            logger.info("\n✅ 所有股票都有历史行情数据！")
            return {'total_count': 0}
        
        # 2. 按市场统计
        logger.info("\n按市场统计:")
        market_stats = db_manager.execute_query(COUNT_BY_MARKET_SQL)
        for stat in market_stats:
            market = stat['market'] or '未知'
            count = stat['count']
            percentage = (count / total_count * 100) if total_count > 0 else 0
            logger.info(f"  {market:<8}: {count:>5} 只 ({percentage:>5.1f}%)")
        
        # 3. 按企业性质统计（前10名）
        logger.info("\n按企业性质统计（前10名）:")
        company_type_stats = db_manager.execute_query(COUNT_BY_COMPANY_TYPE_SQL)
        for i, stat in enumerate(company_type_stats[:10], 1):
            company_type = stat['company_type'] or '未知'
            count = stat['count']
            percentage = (count / total_count * 100) if total_count > 0 else 0
            logger.info(f"  {i:>2}. {company_type:<20}: {count:>5} 只 ({percentage:>5.1f}%)")
        
        logger.info("\n" + "=" * 80)
        
        return {
            'total_count': total_count,
            'market_stats': market_stats,
            'company_type_stats': company_type_stats
        }
        
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        result = query_stocks_without_daily_data()
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)
