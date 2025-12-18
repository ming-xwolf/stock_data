#!/usr/bin/env python3
"""
获取 ETF 基金列表并存入数据库

使用 AKShare API 获取场内 ETF 基金列表，并将基本信息存入数据库。
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
from src.services.etf_service import ETFService

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
        description='获取 ETF 基金列表并存入数据库'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=500,
        help='批量插入的批次大小（默认: 500）'
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
    etf_service = ETFService()
    
    # 获取当前 ETF 数量
    current_count = etf_service.count_etfs()
    logger.info(f"当前数据库中的 ETF 数量: {current_count}")
    
    try:
        # 获取 ETF 列表
        logger.info("开始从 AKShare 获取 ETF 列表...")
        etfs = AKShareClient.get_etf_list()
        
        if not etfs:
            logger.error("未获取到 ETF 数据")
            sys.exit(1)
        
        logger.info(f"成功获取 {len(etfs)} 只 ETF")
        
        # 批量插入数据
        logger.info("开始批量插入 ETF 数据到数据库...")
        
        # 分批处理
        batch_size = args.batch_size
        total_inserted = 0
        
        for i in range(0, len(etfs), batch_size):
            batch = etfs[i:i + batch_size]
            try:
                affected_rows = etf_service.batch_insert_etfs(batch)
                total_inserted += len(batch)
                logger.info(
                    f"已处理 {min(i + batch_size, len(etfs))}/{len(etfs)} 只 ETF"
                )
            except Exception as e:
                logger.error(f"批量插入第 {i//batch_size + 1} 批数据失败: {e}")
                raise
        
        # 统计最终结果
        final_count = etf_service.count_etfs()
        logger.info(f"数据更新完成！")
        logger.info(f"本次处理: {len(etfs)} 只 ETF")
        logger.info(f"数据库当前 ETF 数量: {final_count}")
        
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
