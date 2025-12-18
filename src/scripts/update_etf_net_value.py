#!/usr/bin/env python3
"""
使用 AKShare 更新 ETF 净值数据

使用 fund_etf_fund_info_em API 获取 ETF 的历史净值数据。
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
from src.services.etf_net_value_service import ETFNetValueService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def update_single_etf(code: str, start_date: str = None, end_date: str = None, delay: float = 0.0):
    """
    更新单只 ETF 的净值数据
    
    Args:
        code: ETF 代码
        start_date: 开始日期（YYYY-MM-DD或YYYYMMDD格式）
        end_date: 结束日期（YYYY-MM-DD或YYYYMMDD格式）
        delay: API调用延迟（秒）
    """
    net_value_service = ETFNetValueService()
    
    logger.info(f"开始更新 ETF {code} 的净值数据...")
    
    # 检查是否需要更新（避免不必要的API调用）
    if start_date is None:
        latest_date = net_value_service.get_latest_date(code)
        if latest_date:
            latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
            end_dt = datetime.now().date()
            if latest_dt.date() >= end_dt:
                logger.info(f"✓ ETF {code} 净值已是最新数据（最新日期: {latest_date}），跳过更新")
                return True
            # 从最新日期的下一天开始
            start_date = (latest_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            logger.info(f"从最新日期后续更新: {start_date}")
    
    # 添加延迟（如果需要）
    if delay > 0:
        time.sleep(delay)
    
    try:
        # 获取净值数据
        net_values = AKShareClient.get_etf_net_value(
            code=code,
            start_date=start_date,
            end_date=end_date
        )
        
        if not net_values:
            logger.warning(f"✗ ETF {code} 未获取到净值数据")
            return False
        
        # 批量插入数据库
        affected_rows = net_value_service.batch_insert_net_value(net_values)
        logger.info(f"✓ ETF {code} 净值数据更新成功，插入/更新 {len(net_values)} 条记录")
        return True
        
    except Exception as e:
        logger.error(f"✗ ETF {code} 净值数据更新失败: {e}")
        return False


def update_all_etfs(start_date: str = None, end_date: str = None,
                   batch_size: int = 10, delay: float = 1.0):
    """
    批量更新所有 ETF 的净值数据
    
    优化策略：
    1. 自动检测每只 ETF 的最新日期，只获取新数据
    2. 跳过已是最新数据的 ETF（不调用API）
    3. 添加延迟避免API限流
    """
    etf_service = ETFService()
    net_value_service = ETFNetValueService()
    
    # 获取所有 ETF 列表
    logger.info("获取 ETF 列表...")
    etfs = etf_service.get_all_etfs()
    
    if not etfs:
        logger.error("未获取到 ETF 列表，请先运行 fetch_etfs.py")
        return
    
    logger.info(f"找到 {len(etfs)} 只 ETF，开始批量更新净值数据...")
    logger.info(f"API延迟设置: {delay} 秒")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, etf in enumerate(etfs, 1):
        code = etf['code']
        
        if i % batch_size == 0:
            logger.info(f"已处理 {i}/{len(etfs)} 只 ETF（成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count}）...")
        
        try:
            # 优化：在调用API前检查是否需要更新
            effective_start_date = start_date
            if start_date is None:
                latest_date = net_value_service.get_latest_date(code)
                if latest_date:
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    end_dt = datetime.now().date()
                    if latest_dt.date() >= end_dt:
                        skipped_count += 1
                        continue
                    # 从最新日期的下一天开始
                    effective_start_date = (latest_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            
            success = update_single_etf(
                code=code,
                start_date=effective_start_date,
                end_date=end_date,
                delay=delay
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"更新 ETF {code} 失败: {e}")
            failed_count += 1
            continue
    
    logger.info("="*60)
    logger.info("批量更新完成")
    logger.info(f"成功: {success_count} 只")
    logger.info(f"失败: {failed_count} 只")
    logger.info(f"跳过（已是最新）: {skipped_count} 只")
    logger.info(f"总计: {len(etfs)} 只")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='使用 AKShare 更新 ETF 净值数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 更新单只 ETF（从最新日期开始）
  python src/scripts/update_etf_net_value.py --code 510050
  
  # 更新单只 ETF（指定日期范围）
  python src/scripts/update_etf_net_value.py --code 510050 --start-date 20230101 --end-date 20231201
  
  # 更新所有 ETF（从最新日期开始，自动跳过已是最新的）
  python src/scripts/update_etf_net_value.py --all
  
  # 更新所有 ETF（自定义延迟）
  python src/scripts/update_etf_net_value.py --all --delay 1.5
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
                delay=0.0  # 单只 ETF 不需要延迟
            )
        else:
            # 批量更新所有 ETF
            update_all_etfs(
                start_date=args.start_date,
                end_date=args.end_date,
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
