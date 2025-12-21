#!/usr/bin/env python3
"""
生成股票K线图脚本

支持日线、周线、月线、季线、年线的K线图生成，包含MACD和BOLL指标。
"""
import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
# 脚本位于 src/scripts/，需要向上两级到达项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.charts.stock_chart import StockChartGenerator, DEFAULT_PERIOD

# 默认配置常量
DEFAULT_STOCK_CODE = "600519"  # 默认股票代码（贵州茅台）
DEFAULT_START_DATE = "2000-01-01"  # 默认开始日期提示

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
        description="生成股票K线图（支持日线、周线、月线、季线、年线）"
    )
    parser.add_argument(
        "--code",
        type=str,
        default=DEFAULT_STOCK_CODE,
        help=f"股票代码（默认: {DEFAULT_STOCK_CODE}）",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help=f"开始日期 YYYY-MM-DD（可选，默认从{DEFAULT_START_DATE}开始）",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="结束日期 YYYY-MM-DD（可选，默认使用当前日期）",
    )
    parser.add_argument(
        "--period",
        type=str,
        choices=["D", "W", "M", "Q", "Y"],
        default=DEFAULT_PERIOD,
        help="周期类型：D=日线, W=周线, M=月线, Q=季线, Y=年线（默认: D）",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="图表保存目录（默认: generated_charts）",
    )
    parser.add_argument(
        "--data-source",
        type=str,
        choices=["supabase"],
        default="supabase",
        help="数据源：supabase=Supabase数据库（默认: supabase）",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["png", "svg"],
        default="png",
        help="图片格式：png=PNG位图格式, svg=SVG矢量格式（默认: png）",
    )

    args = parser.parse_args()

    try:
        # 创建图表生成器实例
        generator = StockChartGenerator(image_format=args.format)
        
        # 生成图表
        filepath = generator.generate(
            stock_code=args.code,
            start_date=args.start,
            end_date=args.end,
            period=args.period,
            image_format=args.format
        )
        logger.info(f"图表生成成功: {filepath}")
    except Exception as e:
        logger.error(f"生成图表失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
