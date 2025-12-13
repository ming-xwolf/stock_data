#!/usr/bin/env python3
"""
使用AKShare更新A股交易日历

获取A股交易日历并更新到数据库。
"""
import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.trading_calendar_service import TradingCalendarService
from src.db import db_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def update_trading_calendar(force_update: bool = False):
    """
    更新交易日历
    
    Args:
        force_update: 是否强制更新所有数据（忽略已有数据）
    """
    service = TradingCalendarService()
    
    if force_update:
        logger.info("强制更新模式：将更新所有交易日历数据...")
        success = service.fetch_and_save(update_existing=True)
    else:
        logger.info("智能更新模式：只更新新数据...")
        success = service.update_trading_calendar()
    
    if success:
        logger.info("✓ 交易日历更新成功")
        
        # 显示最新交易日
        latest_date = service.get_latest_trading_date()
        if latest_date:
            logger.info(f"最新交易日: {latest_date}")
    else:
        logger.error("✗ 交易日历更新失败")
    
    return success


def check_trading_date(date: str):
    """
    检查指定日期是否为交易日
    
    Args:
        date: 日期字符串（YYYY-MM-DD格式）
    """
    service = TradingCalendarService()
    is_trading = service.is_trading_date(date)
    
    if is_trading:
        logger.info(f"✓ {date} 是交易日")
    else:
        logger.info(f"✗ {date} 不是交易日")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='使用AKShare更新A股交易日历',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 智能更新（只更新新数据）
  python src/update_trading_calendar.py
  
  # 强制更新所有数据
  python src/update_trading_calendar.py --force
  
  # 检查指定日期是否为交易日
  python src/update_trading_calendar.py --check-date 2024-01-01
  
  # 测试数据库连接
  python src/update_trading_calendar.py --test-connection
        """
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制更新所有数据（忽略已有数据）'
    )
    
    parser.add_argument(
        '--check-date',
        type=str,
        help='检查指定日期是否为交易日（YYYY-MM-DD格式）'
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
    
    # 执行操作
    try:
        if args.check_date:
            # 检查指定日期
            check_trading_date(args.check_date)
        else:
            # 更新交易日历
            success = update_trading_calendar(force_update=args.force)
            if not success:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
