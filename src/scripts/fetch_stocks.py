#!/usr/bin/env python3
"""
获取A股股票列表并存入数据库

使用AKShare API获取A股股票列表，并将基本信息存入Dolt数据库。
"""
import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.clients.akshare_client import AKShareClient
from src.core.db import db_manager
from src.services.stock_service import StockService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='获取A股股票列表并存入数据库'
    )
    parser.add_argument(
        '--with-list-date',
        action='store_true',
        help='是否获取上市日期（较慢）'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='批量插入的批次大小（默认: 1000）'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='仅测试数据库连接'
    )
    
    args = parser.parse_args()
    
    # 测试数据库连接
    logger.info("测试数据库连接...")
    if not db_manager.test_connection():
        logger.error("数据库连接失败，请检查配置和数据库服务")
        sys.exit(1)
    logger.info("数据库连接成功")
    
    if args.test_connection:
        logger.info("数据库连接测试通过")
        return
    
    # 创建服务实例
    stock_service = StockService()
    
    # 获取当前股票数量
    current_count = stock_service.count_stocks()
    logger.info(f"当前数据库中的股票数量: {current_count}")
    
    try:
        # 获取股票列表
        logger.info("开始从AKShare获取股票列表...")
        stocks = AKShareClient.get_stock_list()
        
        if not stocks:
            logger.error("未获取到股票数据")
            sys.exit(1)
        
        logger.info(f"成功获取 {len(stocks)} 只股票")
        
        # 如果需要获取上市日期
        if args.with_list_date:
            logger.info("开始获取股票上市日期（这可能需要一些时间）...")
            stocks = AKShareClient.enrich_stock_info(stocks, include_list_date=True)
        
        # 批量插入数据
        logger.info("开始批量插入股票数据到数据库...")
        
        # 分批处理
        batch_size = args.batch_size
        total_inserted = 0
        
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            try:
                affected_rows = stock_service.batch_insert_stocks(batch)
                total_inserted += len(batch)
                logger.info(
                    f"已处理 {min(i + batch_size, len(stocks))}/{len(stocks)} 只股票"
                )
            except Exception as e:
                logger.error(f"批量插入第 {i//batch_size + 1} 批数据失败: {e}")
                raise
        
        # 统计最终结果
        final_count = stock_service.count_stocks()
        logger.info(f"数据更新完成！")
        logger.info(f"本次处理: {len(stocks)} 只股票")
        logger.info(f"数据库当前股票数量: {final_count}")
        
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

