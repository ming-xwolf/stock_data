#!/usr/bin/env python3
"""
涨跌停查询脚本

用户可以输入起始时间查询个股的涨跌停详细信息。
涨跌停的判断逻辑根据上海、深圳、北交所的要求进行计算。

涨跌幅限制规则：
- 上海主板(60开头): 10%
- 深圳主板(00开头): 10%
- 深圳创业板(30开头): 20%
- 上海科创板(68开头): 20%
- 北交所(8开头,92开头): 30%
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.limit_service import LimitService
from src.db import db_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """格式化数字"""
    if value is None:
        return 'N/A'
    return f"{value:,.{decimals}f}"


def format_volume(value: Optional[int]) -> str:
    """格式化成交量"""
    if value is None:
        return 'N/A'
    if value >= 100000000:
        return f"{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"{value / 10000:.2f}万"
    else:
        return f"{value:,}"


def format_amount(value: Optional[float]) -> str:
    """格式化成交额"""
    if value is None:
        return 'N/A'
    if value >= 100000000:
        return f"{value / 100000000:.2f}亿"
    elif value >= 10000:
        return f"{value / 10000:.2f}万"
    else:
        return f"{value:,.2f}"


def print_limit_stocks(records: list, show_details: bool = True):
    """
    打印涨跌停股票信息
    
    Args:
        records: 涨跌停记录列表
        show_details: 是否显示详细信息
    """
    if not records:
        print("未查询到涨跌停记录")
        return
    
    # 统计信息
    limit_up_count = sum(1 for r in records if r.get('limit_status') == '涨停')
    limit_down_count = sum(1 for r in records if r.get('limit_status') == '跌停')
    
    print("=" * 120)
    print(f"涨跌停查询结果统计")
    print(f"涨停: {limit_up_count} 只")
    print(f"跌停: {limit_down_count} 只")
    print(f"总计: {len(records)} 条记录")
    print("=" * 120)
    
    if show_details:
        print("\n详细记录:")
        print("-" * 120)
        print(f"{'日期':<12} {'代码':<8} {'名称':<12} {'市场':<6} {'状态':<6} "
              f"{'前收盘':<10} {'收盘价':<10} {'涨跌幅':<8} {'成交量':<15} {'成交额':<15} {'换手率':<8}")
        print("-" * 120)
        
        for record in records:
            trade_date = record.get('trade_date')
            if isinstance(trade_date, datetime):
                trade_date = trade_date.strftime('%Y-%m-%d')
            elif not isinstance(trade_date, str):
                trade_date = str(trade_date)
            
            code = record.get('code', 'N/A')
            name = record.get('name', 'N/A')
            market = record.get('market', 'N/A')
            limit_status = record.get('limit_status', 'N/A')
            prev_close = record.get('prev_close_price')
            close_price = record.get('close_price')
            change_pct = record.get('change_pct', 0)
            volume = record.get('volume')
            amount = record.get('amount')
            turnover = record.get('turnover')
            
            # 格式化输出
            print(f"{trade_date:<12} {code:<8} {name[:10]:<12} {market:<6} {limit_status:<6} "
                  f"{format_number(prev_close):<10} {format_number(close_price):<10} "
                  f"{change_pct:>6.2f}% {format_volume(volume):<15} {format_amount(amount):<15} "
                  f"{format_number(turnover, 2) if turnover else 'N/A':<8}")
        
        print("-" * 120)
    else:
        # 只显示汇总信息
        print("\n按日期统计:")
        date_stats = {}
        for record in records:
            trade_date = record.get('trade_date')
            if isinstance(trade_date, datetime):
                trade_date = trade_date.strftime('%Y-%m-%d')
            elif not isinstance(trade_date, str):
                trade_date = str(trade_date)
            
            if trade_date not in date_stats:
                date_stats[trade_date] = {'涨停': 0, '跌停': 0}
            
            limit_status = record.get('limit_status')
            if limit_status == '涨停':
                date_stats[trade_date]['涨停'] += 1
            elif limit_status == '跌停':
                date_stats[trade_date]['跌停'] += 1
        
        print(f"{'日期':<12} {'涨停数':<10} {'跌停数':<10} {'合计':<10}")
        print("-" * 50)
        for date in sorted(date_stats.keys(), reverse=True):
            stats = date_stats[date]
            total = stats['涨停'] + stats['跌停']
            print(f"{date:<12} {stats['涨停']:<10} {stats['跌停']:<10} {total:<10}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='查询股票涨跌停信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
涨跌幅限制规则：
- 上海主板(60开头): 10%
- 深圳主板(00开头): 10%
- 深圳创业板(30开头): 20%
- 上海科创板(68开头): 20%
- 北交所(8开头,92开头): 30%

示例：
  # 查询2024-01-01到今天的涨跌停股票
  python src/query_limit_stocks.py --start-date 2024-01-01
  
  # 查询指定日期范围的涨停股票
  python src/query_limit_stocks.py --start-date 2024-01-01 --end-date 2024-01-31 --type 涨停
  
  # 查询指定股票的涨跌停历史
  python src/query_limit_stocks.py --code 000001 --start-date 2024-01-01
        """
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        required=False,
        help='起始日期（YYYY-MM-DD格式）'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='结束日期（YYYY-MM-DD格式），默认为今天'
    )
    
    parser.add_argument(
        '--code',
        type=str,
        default=None,
        help='股票代码（如果指定，则只查询该股票的涨跌停历史）'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['涨停', '跌停'],
        default=None,
        help='涨跌停类型（涨停/跌停），如果不指定则查询所有'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='只显示汇总信息，不显示详细记录'
    )
    
    parser.add_argument(
        '--statistics',
        action='store_true',
        help='显示统计信息'
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
    
    # 如果不是测试连接，则必须提供起始日期
    if not args.start_date:
        logger.error("必须提供 --start-date 参数（除非使用 --test-connection）")
        sys.exit(1)
    
    # 验证日期格式
    try:
        datetime.strptime(args.start_date, '%Y-%m-%d')
        if args.end_date:
            datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError as e:
        logger.error(f"日期格式错误: {e}，请使用 YYYY-MM-DD 格式")
        sys.exit(1)
    
    # 创建服务实例
    limit_service = LimitService()
    
    try:
        if args.code:
            # 查询指定股票的涨跌停历史
            logger.info(f"查询股票 {args.code} 的涨跌停历史...")
            records = limit_service.query_stock_limit_history(
                args.code,
                args.start_date,
                args.end_date
            )
            
            # 过滤涨跌停类型
            if args.type:
                records = [r for r in records if r.get('limit_status') == args.type]
        else:
            # 查询所有股票的涨跌停记录
            logger.info(f"查询日期范围 {args.start_date} 到 {args.end_date or '今天'} 的涨跌停股票...")
            records = limit_service.query_limit_stocks(
                args.start_date,
                args.end_date,
                args.type
            )
        
        # 显示统计信息
        if args.statistics:
            stats = limit_service.get_limit_statistics(args.start_date, args.end_date)
            print("\n" + "=" * 60)
            print("涨跌停统计信息")
            print("=" * 60)
            print(f"涨停总数: {stats['total_limit_up']}")
            print(f"跌停总数: {stats['total_limit_down']}")
            print(f"总记录数: {stats['total_records']}")
            print("\n按日期统计涨停:")
            for date, count in sorted(stats['limit_up_by_date'].items(), reverse=True):
                print(f"  {date}: {count} 只")
            print("\n按日期统计跌停:")
            for date, count in sorted(stats['limit_down_by_date'].items(), reverse=True):
                print(f"  {date}: {count} 只")
            print("=" * 60)
        
        # 显示查询结果
        print_limit_stocks(records, show_details=not args.summary)
        
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
