#!/usr/bin/env python3
"""
使用AKShare更新股票日线行情数据

优先使用 stock_zh_a_daily (新浪) API，包含成交量和更多字段（流通股本、换手率）。
备选方案：stock_zh_a_hist_tx (腾讯) 和 stock_zh_a_hist_min_em (东方财富) API。
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
                        adjust: str = 'qfq', use_minute: bool = False, use_sina: bool = True,
                        delay: float = 0.0):
    """
    更新单只股票的日线数据
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        adjust: 复权方式
        use_minute: 是否使用分时API
        use_sina: 是否使用新浪API
        delay: API调用延迟（秒），单只股票更新通常不需要延迟
    """
    # 创建服务实例，设置API延迟
    service = DailyQuoteService(api_delay=delay)
    
    logger.info(f"开始更新股票 {code} 的日线数据...")
    
    # 检查是否需要更新（避免不必要的API调用）
    if start_date is None:
        latest_date = service.get_latest_date(code)
        if latest_date:
            latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
            end_dt = datetime.now().date()
            if latest_dt.date() >= end_dt:
                logger.info(f"✓ 股票 {code} 已是最新数据（最新日期: {latest_date}），跳过更新")
                return True
    
    # 添加延迟（如果需要）
    if delay > 0:
        time.sleep(delay)
    
    success = service.fetch_and_save(
        code=code,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
        use_minute=use_minute,
        use_sina=use_sina
    )
    
    if success:
        logger.info(f"✓ 股票 {code} 日线数据更新成功")
    else:
        logger.warning(f"✗ 股票 {code} 日线数据更新失败")
    
    return success


def update_all_stocks(start_date: str = None, end_date: str = None,
                     adjust: str = 'qfq', use_minute: bool = False,
                     use_sina: bool = True,
                     batch_size: int = 10, delay: float = 2.0):
    """
    批量更新所有股票的日线数据
    
    优化策略：
    1. 自动检测每只股票的最新日期，只获取新数据
    2. 跳过已是最新数据的股票（不调用API）
    3. 添加延迟避免API限流（默认2秒，新浪API建议更保守）
    4. 记录跳过和失败的统计
    5. 服务类内置延迟控制，确保API调用间隔
    """
    stock_service = StockService()
    # 创建服务实例，设置API延迟（服务类内部也会控制延迟）
    quote_service = DailyQuoteService(api_delay=delay)
    
    # 获取所有股票列表
    logger.info("获取股票列表...")
    stocks = stock_service.get_all_stocks()
    
    if not stocks:
        logger.error("未获取到股票列表")
        return
    
    logger.info(f"找到 {len(stocks)} 只股票，开始批量更新...")
    logger.info(f"API延迟设置: {delay} 秒（建议 >= 2.0 秒以避免新浪API封IP）")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0  # 跳过的股票（已是最新数据）
    
    for i, stock in enumerate(stocks, 1):
        code = stock['code']
        
        if i % batch_size == 0:
            logger.info(f"已处理 {i}/{len(stocks)} 只股票（成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count}）...")
        
        try:
            # 优化：在调用API前先检查是否需要更新（减少不必要的API调用）
            if start_date is None:
                # 如果没有指定开始日期，检查是否已是最新数据
                latest_date = quote_service.get_latest_date(code)
                if latest_date:
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    end_dt = datetime.now().date()
                    # 如果最新日期 >= 今天，说明已是最新数据，跳过API调用
                    if latest_dt.date() >= end_dt:
                        skipped_count += 1
                        continue
            
            # 注意：延迟控制由服务类内部处理
            # 服务类的 _wait_for_rate_limit() 会确保API调用间隔
            
            success = quote_service.fetch_and_save(
                code=code,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
                use_minute=use_minute,
                use_sina=use_sina
            )
            
            if success:
                success_count += 1
            else:
                # fetch_and_save 返回 False 可能是：
                # 1. 已是最新数据（在fetch_and_save内部已检查并返回True）
                # 2. API调用失败
                # 3. 日期范围无效
                # 这里简化处理，计入失败（实际可能是跳过，但已在fetch_and_save中处理）
                failed_count += 1
                
        except Exception as e:
            logger.error(f"更新股票 {code} 失败: {e}")
            failed_count += 1
            continue
    
    logger.info("="*60)
    logger.info("批量更新完成")
    logger.info(f"成功: {success_count} 只")
    logger.info(f"失败: {failed_count} 只")
    logger.info(f"跳过（已是最新）: {skipped_count} 只")
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
  
  # 更新所有股票（从最新日期开始，自动跳过已是最新的股票）
  python src/update_akshare_daily.py --all
  
  # 更新所有股票（自定义延迟，建议 >= 2.0 秒以避免新浪API封IP）
  python src/update_akshare_daily.py --all --delay 2.5
  
  # 使用分时API获取成交量数据（如果新浪API失败）
  python src/update_akshare_daily.py --code 000001 --use-minute
  
  # 不使用新浪API（使用腾讯API作为备选）
  python src/update_akshare_daily.py --code 000001 --no-sina
  
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
        '--no-sina',
        action='store_true',
        help='不使用新浪API（默认优先使用新浪API，包含成交量和更多字段）'
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
        default=2.0,
        help='每次API调用之间的延迟（秒，默认: 2.0）。新浪API建议 >= 2.0 秒以避免封IP'
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
        use_sina = not args.no_sina  # 默认使用新浪API
        
        if args.code:
            # 更新单只股票（单只股票通常不需要延迟）
            update_single_stock(
                code=args.code,
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_minute=args.use_minute,
                use_sina=use_sina,
                delay=0.0  # 单只股票不需要延迟
            )
        else:
            # 批量更新所有股票
            update_all_stocks(
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_minute=args.use_minute,
                use_sina=use_sina,
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
