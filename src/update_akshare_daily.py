#!/usr/bin/env python3
"""
使用AKShare更新股票日线行情数据

使用 stock_zh_a_hist_tx (腾讯) 和 stock_zh_a_hist_min_em (东方财富) API
获取历史行情数据并更新到数据库。
"""
import argparse
import logging
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.akshare_daily_service import DailyQuoteService
from src.db import db_manager
from src.stock_service import StockService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def update_single_stock(code: str, start_date: str = None, end_date: str = None, 
                        adjust: str = 'qfq', use_minute: bool = False):
    """更新单只股票的日线数据"""
    service = DailyQuoteService()
    
    logger.info(f"开始更新股票 {code} 的日线数据...")
    
    success = service.fetch_and_save(
        code=code,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        use_minute=use_minute
    )
    
    if success:
        logger.info(f"✓ 股票 {code} 日线数据更新成功")
    else:
        logger.warning(f"✗ 股票 {code} 日线数据更新失败")
    
    return success


def update_all_stocks(start_date: str = None, end_date: str = None,
                     adjust: str = 'qfq', use_minute: bool = False,
                     batch_size: int = 10, delay: float = 1.0):
    """批量更新所有股票的日线数据"""
    stock_service = StockService()
    quote_service = DailyQuoteService()
    
    # 获取所有股票列表
    logger.info("获取股票列表...")
    stocks = stock_service.get_all_stocks()
    
    if not stocks:
        logger.error("未获取到股票列表")
        return
    
    logger.info(f"找到 {len(stocks)} 只股票，开始批量更新...")
    
    success_count = 0
    failed_count = 0
    
    for i, stock in enumerate(stocks, 1):
        code = stock['code']
        
        if i % batch_size == 0:
            logger.info(f"已处理 {i}/{len(stocks)} 只股票...")
        
        try:
            success = quote_service.fetch_and_save(
                code=code,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
                use_minute=use_minute
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # 添加延迟，避免API限流
            if delay > 0:
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"更新股票 {code} 失败: {e}")
            failed_count += 1
            continue
    
    logger.info("="*60)
    logger.info("批量更新完成")
    logger.info(f"成功: {success_count} 只")
    logger.info(f"失败: {failed_count} 只")
    logger.info(f"总计: {len(stocks)} 只")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='使用AKShare更新股票日线行情数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 更新单只股票（从最新日期开始）
  python src/update_akshare_daily.py --code 000001
  
  # 更新单只股票（指定日期范围）
  python src/update_akshare_daily.py --code 000001 --start-date 20230101 --end-date 20231201
  
  # 更新所有股票（从最新日期开始）
  python src/update_akshare_daily.py --all
  
  # 使用分时API获取成交量数据
  python src/update_akshare_daily.py --code 000001 --use-minute
  
  # 使用后复权数据
  python src/update_akshare_daily.py --code 000001 --adjust hfq
        """
    )
    
    parser.add_argument(
        '--code',
        type=str,
        help='股票代码（6位数字）'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='更新所有股票'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='开始日期（YYYYMMDD格式），如果不指定则从最新日期开始'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='结束日期（YYYYMMDD格式），如果不指定则使用今天'
    )
    
    parser.add_argument(
        '--adjust',
        type=str,
        choices=['qfq', 'hfq', ''],
        default='qfq',
        help='复权方式：qfq=前复权, hfq=后复权, 空=不复权（默认: qfq）'
    )
    
    parser.add_argument(
        '--use-minute',
        action='store_true',
        help='使用分时API（可以获取成交量数据，但速度较慢）'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='批量更新时的批次大小（默认: 10）'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='每次API调用之间的延迟（秒，默认: 1.0）'
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
    
    # 检查参数
    if not args.code and not args.all:
        parser.print_help()
        logger.error("请指定 --code 或 --all")
        sys.exit(1)
    
    if args.code and args.all:
        logger.error("不能同时指定 --code 和 --all")
        sys.exit(1)
    
    # 执行更新
    try:
        if args.code:
            # 更新单只股票
            update_single_stock(
                code=args.code,
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_minute=args.use_minute
            )
        else:
            # 批量更新所有股票
            update_all_stocks(
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_minute=args.use_minute,
                batch_size=args.batch_size,
                delay=args.delay
            )
    
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
