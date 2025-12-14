#!/usr/bin/env python3
"""
使用Tushare更新股票日线行情数据

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

from src.services.tushare_daily_service import TushareDailyService
from src.core.db import db_manager
from src.services.stock_service import StockService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


# 全局变量：保存失败代码的文件路径
_failed_codes_file = None


def get_failed_codes_file() -> str:
    """
    获取失败代码文件路径（单例模式）
    
    Returns:
        失败代码文件路径
    """
    global _failed_codes_file
    if _failed_codes_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        _failed_codes_file = f"failed_codes_{timestamp}.txt"
    return _failed_codes_file


def save_failed_code(code: str, output_file: str = None):
    """
    立即保存单个失败的股票代码到文件（追加模式）
    
    Args:
        code: 失败的股票代码
        output_file: 输出文件路径，如果为None则使用默认路径
    """
    if not code:
        return
    
    if output_file is None:
        output_file = get_failed_codes_file()
    
    try:
        # 使用追加模式，确保不会覆盖已有内容
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{code}\n")
        logger.debug(f"失败的股票代码 {code} 已追加到文件: {output_file}")
    except Exception as e:
        logger.error(f"保存失败股票代码 {code} 失败: {e}")


def save_failed_codes(failed_codes: list, output_file: str = None):
    """
    保存失败的股票代码列表到文件（批量保存）
    
    Args:
        failed_codes: 失败的股票代码列表
        output_file: 输出文件路径，如果为None则使用默认路径
    """
    if not failed_codes:
        return
    
    if output_file is None:
        output_file = get_failed_codes_file()
    
    try:
        # 使用追加模式，确保不会覆盖已有内容
        with open(output_file, 'a', encoding='utf-8') as f:
            for code in failed_codes:
                f.write(f"{code}\n")
        logger.info(f"失败的股票代码已保存到: {output_file}")
        logger.info(f"共 {len(failed_codes)} 只股票")
    except Exception as e:
        logger.error(f"保存失败股票代码失败: {e}")


def load_failed_codes(input_file: str) -> list:
    """
    从文件加载失败的股票代码
    
    Args:
        input_file: 输入文件路径
        
    Returns:
        股票代码列表
    """
    codes = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                code = line.strip()
                if code and code.isdigit() and len(code) == 6:
                    codes.append(code)
        logger.info(f"从文件加载了 {len(codes)} 只股票代码: {input_file}")
        return codes
    except Exception as e:
        logger.error(f"加载失败股票代码失败: {e}")
        return []


def update_single_stock(code: str, start_date: str = None, end_date: str = None):
    """更新单只股票的日线数据"""
    service = TushareDailyService()
    
    logger.info(f"开始更新股票 {code} 的日线数据...")
    
    success = service.fetch_and_save(
        code=code,
        start_date=start_date,
        end_date=end_date
    )
    
    if success:
        logger.info(f"✓ 股票 {code} 日线数据更新成功")
    else:
        logger.warning(f"✗ 股票 {code} 日线数据更新失败")
    
    return success


def save_failed_codes(failed_codes: list, output_file: str = None):
    """
    保存失败的股票代码到文件
    
    Args:
        failed_codes: 失败的股票代码列表
        output_file: 输出文件路径，如果为None则使用默认路径
    """
    if not failed_codes:
        return
    
    if output_file is None:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"failed_codes_{timestamp}.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for code in failed_codes:
                f.write(f"{code}\n")
        logger.info(f"失败的股票代码已保存到: {output_file}")
        logger.info(f"共 {len(failed_codes)} 只股票")
    except Exception as e:
        logger.error(f"保存失败股票代码失败: {e}")


def load_failed_codes(input_file: str) -> list:
    """
    从文件加载失败的股票代码
    
    Args:
        input_file: 输入文件路径
        
    Returns:
        股票代码列表
    """
    codes = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                code = line.strip()
                if code and code.isdigit() and len(code) == 6:
                    codes.append(code)
        logger.info(f"从文件加载了 {len(codes)} 只股票代码: {input_file}")
        return codes
    except Exception as e:
        logger.error(f"加载失败股票代码失败: {e}")
        return []


def update_all_stocks(start_date: str = None, end_date: str = None,
                     batch_size: int = 10, delay: float = 0.0,
                     save_failed: bool = True):
    """批量更新所有股票的日线数据"""
    stock_service = StockService()
    quote_service = TushareDailyService()
    
    # 获取所有股票列表
    logger.info("获取股票列表...")
    stocks = stock_service.get_all_stocks()
    
    if not stocks:
        logger.error("未获取到股票列表")
        return
    
    logger.info(f"找到 {len(stocks)} 只股票，开始批量更新...")
    
    codes = [stock['code'] for stock in stocks]
    
    # 如果启用保存失败代码，初始化文件
    failed_codes_file = None
    if save_failed:
        failed_codes_file = get_failed_codes_file()
        logger.info(f"失败的股票代码将实时保存到: {failed_codes_file}")
        # 清空文件（如果存在），开始新的记录
        try:
            with open(failed_codes_file, 'w', encoding='utf-8') as f:
                f.write(f"# 失败股票代码列表 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        except Exception as e:
            logger.warning(f"初始化失败代码文件失败: {e}")
    
    # 分批处理
    success_count = 0
    failed_count = 0
    all_failed_codes = []
    
    for i in range(0, len(codes), batch_size):
        batch_codes = codes[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(codes) + batch_size - 1) // batch_size
        
        logger.info(f"处理批次 {batch_num}/{total_batches} ({len(batch_codes)} 只股票)...")
        
        result = quote_service.batch_update(
            codes=batch_codes,
            start_date=start_date,
            end_date=end_date,
            delay=delay,
            failed_codes_file=failed_codes_file
        )
        
        success_count += result['success_count']
        failed_count += result['failed_count']
        all_failed_codes.extend(result.get('failed_codes', []))
        
        # 批次之间的延迟（批次间使用更长的延迟，确保不会触发限制）
        if i + batch_size < len(codes):
            # 客户端已有1.3秒延迟，批次间额外等待1秒，确保稳定
            batch_delay = max(delay + 1.0, 1.0)  # 至少1秒
            logger.info(f"等待 {batch_delay:.1f} 秒后继续下一批次...")
            time.sleep(batch_delay)
    
    logger.info("="*60)
    logger.info("批量更新完成")
    logger.info(f"成功: {success_count} 只")
    logger.info(f"失败: {failed_count} 只")
    logger.info(f"总计: {len(codes)} 只")
    
    # 显示失败代码文件信息
    if save_failed and failed_codes_file:
        try:
            # 统计文件中的失败代码数量（排除注释行）
            with open(failed_codes_file, 'r', encoding='utf-8') as f:
                file_codes = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            if file_codes:
                logger.info(f"失败的股票代码已保存到: {failed_codes_file}")
                logger.info(f"文件中共 {len(file_codes)} 只失败的股票")
        except Exception as e:
            logger.warning(f"读取失败代码文件失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='使用Tushare更新股票日线行情数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 更新单只股票（从最新日期开始）
  python src/update_tushare_daily.py --code 000001
  
  # 更新单只股票（指定日期范围）
  python src/update_tushare_daily.py --code 000001 --start-date 20230101 --end-date 20231201
  
  # 更新所有股票（从最新日期开始）
  python src/update_tushare_daily.py --all
  
  # 更新所有股票（指定日期范围）
  python src/update_tushare_daily.py --all --start-date 20230101 --end-date 20231201
  
  # 自定义批次大小和延迟
  python src/update_tushare_daily.py --all --batch-size 20 --delay 0.0
  
  # 从文件读取失败的股票代码并重新更新
  python src/update_tushare_daily.py --failed-codes-file failed_codes_20231212_200000.txt
  
  # 不保存失败的股票代码
  python src/update_tushare_daily.py --all --no-save-failed
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
        '--batch-size',
        type=int,
        default=10,
        help='批量更新时的批次大小（默认: 10）'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.0,
        help='每次API调用之间的额外延迟（秒，默认: 0.0）。客户端已有1.3秒默认延迟，确保每分钟不超过50次。如需更保守可设置额外延迟。'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='仅测试数据库连接'
    )
    
    parser.add_argument(
        '--failed-codes-file',
        type=str,
        help='从文件读取失败的股票代码并重新更新（每行一个股票代码）'
    )
    
    parser.add_argument(
        '--no-save-failed',
        action='store_true',
        help='不保存失败的股票代码到文件'
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
    if not args.code and not args.all and not args.failed_codes_file:
        parser.print_help()
        logger.error("请指定 --code、--all 或 --failed-codes-file")
        sys.exit(1)
    
    if args.code and args.all:
        logger.error("不能同时指定 --code 和 --all")
        sys.exit(1)
    
    if args.failed_codes_file and (args.code or args.all):
        logger.error("--failed-codes-file 不能与其他选项同时使用")
        sys.exit(1)
    
    # 执行更新
    try:
        if args.failed_codes_file:
            # 从文件读取失败的股票代码并更新
            failed_codes = load_failed_codes(args.failed_codes_file)
            if not failed_codes:
                logger.warning("文件中没有有效的股票代码")
                return
            
            logger.info(f"开始更新 {len(failed_codes)} 只失败的股票...")
            
            # 如果启用保存失败代码，初始化新文件
            retry_failed_codes_file = None
            if not args.no_save_failed:
                retry_failed_codes_file = get_failed_codes_file()
                logger.info(f"重新更新失败的股票代码将实时保存到: {retry_failed_codes_file}")
                # 清空文件（如果存在），开始新的记录
                try:
                    with open(retry_failed_codes_file, 'w', encoding='utf-8') as f:
                        f.write(f"# 重新更新失败的股票代码列表 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                except Exception as e:
                    logger.warning(f"初始化失败代码文件失败: {e}")
            
            quote_service = TushareDailyService()
            result = quote_service.batch_update(
                codes=failed_codes,
                start_date=args.start_date,
                end_date=args.end_date,
                delay=args.delay,
                failed_codes_file=retry_failed_codes_file
            )
            
            logger.info("="*60)
            logger.info("失败股票重新更新完成")
            logger.info(f"成功: {result['success_count']} 只")
            logger.info(f"失败: {result['failed_count']} 只")
            logger.info(f"总计: {result['total']} 只")
            
            # 显示失败代码文件信息
            if retry_failed_codes_file:
                try:
                    # 统计文件中的失败代码数量（排除注释行）
                    with open(retry_failed_codes_file, 'r', encoding='utf-8') as f:
                        file_codes = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                    if file_codes:
                        logger.info(f"仍然失败的股票代码已保存到: {retry_failed_codes_file}")
                        logger.info(f"文件中共 {len(file_codes)} 只失败的股票")
                except Exception as e:
                    logger.warning(f"读取失败代码文件失败: {e}")
        elif args.code:
            # 更新单只股票
            update_single_stock(
                code=args.code,
                start_date=args.start_date,
                end_date=args.end_date
            )
        else:
            # 批量更新所有股票
            update_all_stocks(
                start_date=args.start_date,
                end_date=args.end_date,
                batch_size=args.batch_size,
                delay=args.delay,
                save_failed=not args.no_save_failed
            )
    
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
