#!/usr/bin/env python3
"""
使用 AKShare 更新 ETF 日线行情数据

使用 fund_etf_hist_em API 获取 ETF 的历史行情数据。
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

from src.clients.akshare_client import AKShareClient
from src.core.db import db_manager
from src.services.etf_service import ETFService
from src.services.etf_daily_service import ETFDailyService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def update_single_etf(code: str, start_date: str = None, end_date: str = None,
                     period: str = 'daily', adjust: str = '', delay: float = 0.0):
    """
    更新单只 ETF 的日线数据
    
    Args:
        code: ETF 代码
        start_date: 开始日期（YYYY-MM-DD或YYYYMMDD格式）
        end_date: 结束日期（YYYY-MM-DD或YYYYMMDD格式）
        period: 周期（daily/weekly/monthly）
        adjust: 复权方式（''=不复权, 'qfq'=前复权, 'hfq'=后复权）
        delay: API调用延迟（秒）
    """
    daily_service = ETFDailyService()
    
    logger.info(f"开始更新 ETF {code} 的日线数据...")
    
    # 检查是否需要更新（避免不必要的API调用）
    if start_date is None:
        latest_date = daily_service.get_latest_date(code)
        if latest_date:
            latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
            end_dt = datetime.now().date()
            if latest_dt.date() >= end_dt:
                logger.info(f"✓ ETF {code} 已是最新数据（最新日期: {latest_date}），跳过更新")
                return True
            # 从最新日期的下一天开始
            start_date = (latest_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            logger.info(f"从最新日期后续更新: {start_date}")
    
    # 添加延迟（如果需要）
    if delay > 0:
        time.sleep(delay)
    
    try:
        # 获取日线数据
        daily_data = AKShareClient.get_etf_daily_data(
            code=code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if not daily_data:
            logger.warning(f"✗ ETF {code} 未获取到日线数据")
            return False
        
        # 批量插入数据库
        affected_rows = daily_service.batch_insert_daily_data(daily_data)
        logger.info(f"✓ ETF {code} 日线数据更新成功，插入/更新 {len(daily_data)} 条记录")
        return True
        
    except Exception as e:
        logger.error(f"✗ ETF {code} 日线数据更新失败: {e}")
        return False


def update_all_etfs(start_date: str = None, end_date: str = None,
                   period: str = 'daily', adjust: str = '',
                   batch_size: int = 10, delay: float = 1.0):
    """
    批量更新所有 ETF 的日线数据
    
    优化策略：
    1. 自动检测每只 ETF 的最新日期，只获取新数据
    2. 跳过已是最新数据的 ETF（不调用API）
    3. 添加延迟避免API限流
    """
    etf_service = ETFService()
    daily_service = ETFDailyService()
    
    # 获取所有 ETF 列表
    logger.info("获取 ETF 列表...")
    etfs = etf_service.get_all_etfs()
    
    if not etfs:
        logger.error("未获取到 ETF 列表，请先运行 fetch_etfs.py")
        return
    
    logger.info(f"找到 {len(etfs)} 只 ETF，开始批量更新...")
    logger.info(f"API延迟设置: {delay} 秒")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    for i, etf in enumerate(etfs, 1):
        code = etf['code']
        
        try:
            # 优化：在调用API前检查是否需要更新
            effective_start_date = start_date
            if start_date is None:
                latest_date = daily_service.get_latest_date(code)
                if latest_date:
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    end_dt = datetime.now().date()
                    if latest_dt.date() >= end_dt:
                        skipped_count += 1
                        # 即使跳过也需要打印进度（如果到了批次）
                        if i % batch_size == 0 or i == len(etfs):
                            elapsed = time.time() - start_time
                            avg_time = elapsed / i
                            remaining = avg_time * (len(etfs) - i)
                            remaining_str = str(timedelta(seconds=int(remaining)))
                            logger.info(
                                f"进度: {i}/{len(etfs)} ({i/len(etfs)*100:.1f}%) - "
                                f"成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count} - "
                                f"预计剩余时间: {remaining_str}"
                            )
                        continue
                    # 从最新日期的下一天开始
                    effective_start_date = (latest_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            
            success = update_single_etf(
                code=code,
                start_date=effective_start_date,
                end_date=end_date,
                period=period,
                adjust=adjust,
                delay=delay
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"更新 ETF {code} 失败: {e}")
            failed_count += 1
        
        # 打印进度
        if i % batch_size == 0 or i == len(etfs):
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = avg_time * (len(etfs) - i)
            remaining_str = str(timedelta(seconds=int(remaining)))
            logger.info(
                f"进度: {i}/{len(etfs)} ({i/len(etfs)*100:.1f}%) - "
                f"成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count} - "
                f"预计剩余时间: {remaining_str}"
            )
    
    total_time = str(timedelta(seconds=int(time.time() - start_time)))
    logger.info("="*60)
    logger.info(f"批量更新完成，耗时: {total_time}")
    logger.info(f"成功: {success_count} 只")
    logger.info(f"失败: {failed_count} 只")
    logger.info(f"跳过（已是最新）: {skipped_count} 只")
    logger.info(f"总计: {len(etfs)} 只")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='使用 AKShare 更新 ETF 日线行情数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 更新单只 ETF（从最新日期开始）
  python src/scripts/update_etf_daily.py --code 510050
  
  # 更新单只 ETF（指定日期范围）
  python src/scripts/update_etf_daily.py --code 510050 --start-date 20230101 --end-date 20231201
  
  # 更新所有 ETF（从最新日期开始，自动跳过已是最新的）
  python src/scripts/update_etf_daily.py --all
  
  # 更新所有 ETF（自定义延迟）
  python src/scripts/update_etf_daily.py --all --delay 1.5
  
  # 使用前复权数据
  python src/scripts/update_etf_daily.py --code 510050 --adjust qfq
        """
    )
    
    parser.add_argument(
        '--code',
        type=str,
        help='ETF 代码'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='更新所有 ETF'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='开始日期（YYYYMMDD或YYYY-MM-DD格式），如果不指定则从最新日期开始'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        help='结束日期（YYYYMMDD或YYYY-MM-DD格式），如果不指定则使用今天'
    )
    
    parser.add_argument(
        '--period',
        type=str,
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='周期：daily=日线, weekly=周线, monthly=月线（默认: daily）'
    )
    
    parser.add_argument(
        '--adjust',
        type=str,
        choices=['', 'qfq', 'hfq'],
        default='',
        help='复权方式：空=不复权, qfq=前复权, hfq=后复权（默认: 不复权）'
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
            # 更新单只 ETF
            update_single_etf(
                code=args.code,
                start_date=args.start_date,
                end_date=args.end_date,
                period=args.period,
                adjust=args.adjust,
                delay=0.0  # 单只 ETF 不需要延迟
            )
        else:
            # 批量更新所有 ETF
            update_all_etfs(
                start_date=args.start_date,
                end_date=args.end_date,
                period=args.period,
                adjust=args.adjust,
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
