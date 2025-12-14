#!/usr/bin/env python3
"""
更新股票扩展数据

使用AKShare API获取股票的股东、行业、财务、市值等数据，并存入数据库。
"""
import argparse
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.akshare_client import AKShareClient
from src.db import db_manager
from src.stock_service import StockService
from src.industry_service import IndustryService
from src.shareholder_service import ShareholderService
from src.market_value_service import MarketValueService
from src.financial_service import FinancialService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def update_company_info(code: str, stock_service: StockService, basic_info: Optional[Dict] = None, 
                        controller_info: Optional[Dict] = None) -> bool:
    """
    更新公司信息（企业性质、实际控制人、直接控制人、主营产品）
    
    Args:
        code: 股票代码
        stock_service: 股票服务实例
        basic_info: 基本信息（可选，避免重复调用API）
        controller_info: 控制人信息（可选，批量更新时传入）
    """
    try:
        # 获取基本信息（企业性质、主营业务等）
        if basic_info is None:
            company_info = AKShareClient.get_stock_company_info(code, None)
        else:
            company_info = AKShareClient.get_stock_company_info(code, basic_info)
        
        # 获取控制人信息（如果未提供）
        if controller_info is None:
            controller_info = AKShareClient.get_stock_controller_info(code)
        
        # 合并信息，优先使用 controller_info 中的实际控制人
        if controller_info:
            if controller_info.get('actual_controller'):
                company_info = company_info or {}
                company_info['actual_controller'] = controller_info.get('actual_controller')
            if controller_info.get('direct_controller'):
                company_info = company_info or {}
                company_info['direct_controller'] = controller_info.get('direct_controller')
        
        if company_info:
            result = stock_service.update_company_info(
                code=code,
                company_type=company_info.get('company_type'),
                actual_controller=company_info.get('actual_controller'),
                direct_controller=company_info.get('direct_controller'),
                main_business=company_info.get('main_business')
            )
            if result:
                logger.debug(f"成功更新股票 {code} 公司信息")
            return result
        else:
            logger.debug(f"股票 {code} 未获取到公司信息")
        return False
    except Exception as e:
        logger.error(f"更新股票 {code} 公司信息失败: {e}", exc_info=True)
        return False


def batch_update_controller_info(stocks: List[Dict], stock_service: StockService) -> int:
    """
    批量更新控制人信息
    
    Args:
        stocks: 股票列表
        stock_service: 股票服务实例
        
    Returns:
        成功更新的股票数量
    """
    try:
        logger.info("批量获取所有股票的控制人信息...")
        df = AKShareClient.get_all_controller_data()
        if df is None or df.empty:
            logger.warning("未获取到批量控制人数据，将使用单独更新")
            return 0
        
        # 解析批量数据
        controller_dict = AKShareClient.parse_all_controller_data(df)
        logger.info(f"成功解析 {len(controller_dict)} 只股票的控制人信息")
        
        # 批量更新
        success_count = 0
        for stock in stocks:
            code = stock['code']
            controller_info = controller_dict.get(code)
            
            if controller_info:
                # 只更新控制人信息，不更新其他公司信息
                result = stock_service.update_company_info(
                    code=code,
                    company_type=None,
                    actual_controller=controller_info.get('actual_controller'),
                    direct_controller=controller_info.get('direct_controller'),
                    main_business=None
                )
                if result:
                    success_count += 1
        
        logger.info(f"批量更新控制人信息完成，成功更新 {success_count} 只股票")
        return success_count
    except Exception as e:
        logger.error(f"批量更新控制人信息失败: {e}", exc_info=True)
        return 0


def batch_update_market_value(stocks: List[Dict], market_value_service: MarketValueService) -> int:
    """
    批量更新市值信息
    
    Args:
        stocks: 股票列表
        market_value_service: 市值服务实例
        
    Returns:
        成功更新的股票数量
    """
    try:
        logger.info("批量获取所有股票的市值信息...")
        market_values = AKShareClient.get_all_market_value()
        
        if market_values is None or not market_values:
            logger.warning("未获取到批量市值数据，将使用单独更新")
            return 0
        
        # 转换为字典，便于查找
        market_value_dict = {mv['code']: mv for mv in market_values}
        logger.info(f"成功获取 {len(market_value_dict)} 只股票的市值信息")
        
        # 批量更新
        success_count = 0
        for stock in stocks:
            code = stock['code']
            market_value = market_value_dict.get(code)
            
            if market_value:
                result = market_value_service.insert_market_value(**market_value)
                if result:
                    success_count += 1
        
        logger.info(f"批量更新市值信息完成，成功更新 {success_count} 只股票")
        return success_count
    except Exception as e:
        logger.error(f"批量更新市值信息失败: {e}", exc_info=True)
        return 0


def update_industry_info(code: str, industry_service: IndustryService, basic_info: Optional[Dict] = None) -> bool:
    """更新行业信息"""
    try:
        industry_info = AKShareClient.get_stock_industry_info(code, basic_info)
        if industry_info:
            industry_info['code'] = code
            industry_info['update_date'] = datetime.now().strftime('%Y-%m-%d')
            result = industry_service.insert_industry(**industry_info)
            if result:
                logger.debug(f"成功更新股票 {code} 行业信息")
            return result
        else:
            logger.debug(f"股票 {code} 未获取到行业信息")
        return False
    except Exception as e:
        logger.error(f"更新股票 {code} 行业信息失败: {e}", exc_info=True)
        return False


def update_shareholders(code: str, shareholder_service: ShareholderService) -> bool:
    """更新股东信息"""
    try:
        shareholders = AKShareClient.get_stock_shareholders(code)
        if shareholders:
            # batch_insert_shareholders 使用 ON DUPLICATE KEY UPDATE，
            # 会自动处理已存在的记录（更新）和新记录（插入）
            shareholder_service.batch_insert_shareholders(shareholders)
            logger.debug(f"成功处理股票 {code} 股东信息，共 {len(shareholders)} 条（插入或更新）")
            return True
        else:
            logger.debug(f"股票 {code} 未获取到股东信息")
        return False
    except Exception as e:
        logger.error(f"更新股票 {code} 股东信息失败: {e}", exc_info=True)
        return False


def update_market_value(code: str, market_value_service: MarketValueService) -> bool:
    """更新市值信息"""
    try:
        market_value = AKShareClient.get_stock_market_value(code)
        if market_value:
            result = market_value_service.insert_market_value(**market_value)
            if result:
                logger.debug(f"成功更新股票 {code} 市值信息")
            return result
        else:
            logger.debug(f"股票 {code} 未获取到市值信息")
        return False
    except Exception as e:
        logger.error(f"更新股票 {code} 市值信息失败: {e}", exc_info=True)
        return False


def update_financial_data(code: str, financial_service: FinancialService) -> bool:
    """
    更新财务数据（智能更新：如果数据已是最新则跳过API调用）
    
    策略：
    1. 先检查数据库中的最新报告日期，判断数据是否已是最新
    2. 如果数据已是最新，直接跳过API调用和数据库写入
    3. 如果数据不是最新，调用API获取所有报告期的利润表数据
    4. 检查数据库中是否已有这些报告期的数据
    5. 如果已有完整数据，跳过数据库写入操作（避免重复写入）
    6. 如果数据不完整，只插入/更新缺失的报告期数据
    """
    try:
        # 先检查数据是否已是最新（不调用API）
        if financial_service.is_income_data_up_to_date(code):
            logger.info(f"股票 {code} 利润表数据已是最新，跳过API调用和更新")
            return True
        
        # 如果数据不是最新，调用API获取所有报告期的利润表数据
        income_statements = AKShareClient.get_stock_income_statements(code)
        if not income_statements:
            # 如果新方法失败，尝试使用旧方法（只更新最新一期）
            financial_data = AKShareClient.get_stock_financial_data(code)
            if financial_data and 'income' in financial_data:
                income = financial_data['income']
                result = financial_service.insert_income_statement(
                    code=code,
                    report_date=income.get('report_date'),
                    total_revenue=income.get('total_revenue'),
                    operating_revenue=income.get('operating_revenue'),
                    net_profit=income.get('net_profit'),
                    net_profit_attributable=income.get('net_profit_attributable'),
                )
                return result
            return False
        
        # 检查数据库中是否已有完整数据
        if financial_service.has_complete_income_data(code, income_statements):
            logger.info(f"股票 {code} 利润表数据已完整（共 {len(income_statements)} 期），跳过数据库写入")
            return True
        
        # 获取数据库中已有的报告日期
        db_dates = set(financial_service.get_income_statement_dates(code))
        
        # 只插入数据库中缺失的报告期数据
        success = True
        new_count = 0
        update_count = 0
        
        for income in income_statements:
            report_date = income.get('report_date')
            if not report_date:
                continue
            
            report_date_str = str(report_date)
            
            # 如果数据库中已有该报告日期，使用 ON DUPLICATE KEY UPDATE 更新
            # 如果数据库中没有，则插入新数据
            result = financial_service.insert_income_statement(
                code=income.get('code'),
                report_date=report_date_str,
                report_period=income.get('report_period'),
                report_type=income.get('report_type'),
                total_revenue=income.get('total_revenue'),
                operating_revenue=income.get('operating_revenue'),
                operating_cost=income.get('operating_cost'),
                operating_profit=income.get('operating_profit'),
                total_profit=income.get('total_profit'),
                net_profit=income.get('net_profit'),
                net_profit_attributable=income.get('net_profit_attributable'),
                basic_eps=income.get('basic_eps'),
                diluted_eps=income.get('diluted_eps'),
            )
            
            if result:
                if report_date_str in db_dates:
                    update_count += 1
                else:
                    new_count += 1
            else:
                success = False
        
        if new_count > 0 or update_count > 0:
            logger.info(f"股票 {code} 利润表数据更新完成：新增 {new_count} 期，更新 {update_count} 期，共 {len(income_statements)} 期")
        else:
            logger.debug(f"股票 {code} 利润表数据无需更新")
        
        return success
    except Exception as e:
        logger.error(f"更新股票 {code} 财务数据失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='更新股票扩展数据（股东、行业、财务、市值）'
    )
    parser.add_argument(
        '--code',
        type=str,
        help='股票代码（如：000001），如果不指定则更新所有股票'
    )
    parser.add_argument(
        '--data-type',
        type=str,
        choices=['all', 'company_info', 'industry', 'shareholders', 'market_value', 'financial'],
        default='all',
        help='要更新的数据类型（默认：all）'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='批量处理的股票数量（默认：100）'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='每次API调用之间的延迟（秒，默认：0.5）'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='仅测试数据库连接'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='清除所有API缓存后退出'
    )
    
    args = parser.parse_args()
    
    # 如果指定清除缓存，则清除后退出
    if args.clear_cache:
        logger.info("清除所有API缓存...")
        AKShareClient.clear_caches()
        stats = AKShareClient.get_cache_stats()
        logger.info(f"缓存已清除。缓存统计: {stats}")
        return
    
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
    industry_service = IndustryService()
    shareholder_service = ShareholderService()
    market_value_service = MarketValueService()
    financial_service = FinancialService()
    
    # 确定要处理的股票列表
    if args.code:
        stock = stock_service.get_stock(args.code)
        if not stock:
            logger.error(f"股票 {args.code} 不存在于数据库中，请先运行 fetch_stocks.py")
            sys.exit(1)
        stocks = [stock]
    else:
        stocks = stock_service.get_all_stocks()
        if not stocks:
            logger.error("数据库中没有任何股票，请先运行 fetch_stocks.py")
            sys.exit(1)
    
    logger.info(f"开始更新 {len(stocks)} 只股票的数据...")
    
    # 统计
    stats = {
        'company_info': 0,
        'industry': 0,
        'shareholders': 0,
        'market_value': 0,
        'financial': 0,
        'failed': 0
    }
    
    # 判断是否为批量更新（更新所有股票且数量大于1）
    is_batch_update = args.code is None and len(stocks) > 1
    
    # 如果是批量更新财务数据，先筛选出需要更新的股票
    stocks_to_update_financial = None
    if is_batch_update and args.data_type in ['all', 'financial']:
        logger.info("批量更新财务数据：筛选需要更新的股票...")
        previous_report_date = FinancialService.get_previous_report_date()
        logger.info(f"上一个报告期日期: {previous_report_date}")
        
        stocks_to_update_list = financial_service.get_stocks_without_report_date(previous_report_date)
        if stocks_to_update_list:
            logger.info(f"找到 {len(stocks_to_update_list)} 只股票缺少报告日期 {previous_report_date}，需要更新")
            # 转换为集合便于快速查找
            stocks_to_update_financial = set(stocks_to_update_list)
            # 只保留需要更新的股票
            stocks = [s for s in stocks if s['code'] in stocks_to_update_financial]
            logger.info(f"将更新 {len(stocks)} 只股票的财务数据")
        else:
            logger.info(f"所有股票都已包含报告日期 {previous_report_date}，无需更新财务数据")
            # 如果只更新财务数据，直接退出
            if args.data_type == 'financial':
                logger.info("所有股票的利润表数据已是最新，无需更新")
                return
            # 如果还要更新其他数据，继续执行，但跳过财务数据更新
            stocks_to_update_financial = set()  # 空集合，表示没有股票需要更新
    
    try:
        # ========== 批量更新部分 ==========
        if is_batch_update:
            # 批量更新控制人信息（如果有批量API）
            if args.data_type in ['all', 'company_info']:
                logger.info("使用批量API更新控制人信息...")
                batch_count = batch_update_controller_info(stocks, stock_service)
                stats['company_info'] += batch_count
            
            # 批量更新市值信息（如果有批量API）
            if args.data_type in ['all', 'market_value']:
                logger.info("使用批量API更新市值信息...")
                batch_count = batch_update_market_value(stocks, market_value_service)
                stats['market_value'] += batch_count
        
        # ========== 单独更新部分 ==========
        # 对于没有批量API的数据，或者单个股票更新，使用单独更新
        for i, stock in enumerate(stocks, 1):
            code = stock['code']
            name = stock.get('name', '')
            
            logger.info(f"[{i}/{len(stocks)}] 处理股票 {code} ({name})")
            
            success = True
            
            # 如果需要更新公司信息或行业信息，一次性获取基本信息（避免重复调用）
            basic_info = None
            if args.data_type in ['all', 'company_info', 'industry']:
                try:
                    basic_info = AKShareClient.get_stock_basic_info(code)
                    if basic_info:
                        logger.debug(f"成功获取股票 {code} 基本信息")
                    else:
                        logger.warning(f"股票 {code} 未获取到基本信息")
                    time.sleep(args.delay)  # 只在这里延迟一次
                except Exception as e:
                    logger.error(f"获取股票 {code} 基本信息失败: {e}")
                    basic_info = None
            
            # 更新公司信息（企业性质、实际控制人、主营产品）
            # 如果是批量更新且已批量更新了控制人信息，则只更新其他公司信息（企业性质、主营业务）
            if args.data_type in ['all', 'company_info']:
                # 批量更新时，控制人信息已更新，这里只更新其他信息
                controller_info = None
                if is_batch_update:
                    # 尝试从批量数据中获取控制人信息（避免重复调用）
                    try:
                        df = AKShareClient.get_all_controller_data()
                        if df is not None and not df.empty:
                            controller_dict = AKShareClient.parse_all_controller_data(df)
                            controller_info = controller_dict.get(code)
                    except:
                        pass
                
                # 对于92开头的股票（北交所），需要特别处理企业性质更新
                # 因为批量控制人API可能不包含这些股票，但仍需要更新企业性质
                is_92_stock = code.startswith('92')
                
                # 如果批量更新成功且有控制人信息，这里只更新企业性质和主营业务
                if is_batch_update and controller_info:
                    # 只更新企业性质和主营业务，控制人信息已在批量更新中处理
                    if basic_info is None:
                        # 如果basic_info为空，尝试获取基本信息
                        basic_info = AKShareClient.get_stock_basic_info(code)
                    
                    if basic_info and (basic_info.get('company_type') or basic_info.get('main_business')):
                        result = stock_service.update_company_info(
                            code=code,
                            company_type=basic_info.get('company_type'),
                            actual_controller=None,  # 不更新，已在批量更新中处理
                            direct_controller=None,  # 不更新，已在批量更新中处理
                            main_business=basic_info.get('main_business')
                        )
                        if result:
                            stats['company_info'] = stats.get('company_info', 0) + 1
                        else:
                            stats['failed'] += 1
                            success = False
                    # 如果basic_info仍然为空或没有企业性质，记录日志但不报错
                    elif basic_info is None:
                        logger.debug(f"股票 {code} 无法获取基本信息，跳过企业性质更新")
                # 对于92开头的股票，即使批量更新时没有控制人信息，也要尝试更新企业性质和控制人信息
                elif is_batch_update and is_92_stock:
                    # 92开头的股票，批量控制人API可能不包含，需要单独获取控制人信息
                    if controller_info is None:
                        # 尝试单独获取控制人信息
                        try:
                            controller_info = AKShareClient.get_stock_controller_info(code)
                        except Exception as e:
                            logger.debug(f"获取股票 {code} (92开头) 控制人信息失败: {e}")
                            controller_info = None
                    
                    if basic_info is None:
                        # 获取基本信息（对于92开头股票，会从stock_individual_basic_info_xq获取classi_name）
                        basic_info = AKShareClient.get_stock_basic_info(code)
                    
                    # 更新企业性质、主营业务和控制人信息（如果有）
                    company_type = basic_info.get('company_type') if basic_info else None
                    main_business = basic_info.get('main_business') if basic_info else None
                    actual_controller = controller_info.get('actual_controller') if controller_info else None
                    direct_controller = controller_info.get('direct_controller') if controller_info else None
                    
                    # 如果有任何需要更新的信息，就更新
                    if company_type or main_business or actual_controller or direct_controller:
                        result = stock_service.update_company_info(
                            code=code,
                            company_type=company_type,
                            actual_controller=actual_controller,
                            direct_controller=direct_controller,
                            main_business=main_business
                        )
                        if result:
                            stats['company_info'] = stats.get('company_info', 0) + 1
                            if company_type:
                                logger.debug(f"股票 {code} (92开头) 成功更新企业性质: {company_type}")
                            if actual_controller or direct_controller:
                                logger.debug(f"股票 {code} (92开头) 成功更新控制人信息")
                        else:
                            stats['failed'] += 1
                            success = False
                    else:
                        logger.debug(f"股票 {code} (92开头) 未获取到任何公司信息，跳过更新")
                else:
                    # 非批量更新，使用完整更新
                    if update_company_info(code, stock_service, basic_info, controller_info):
                        stats['company_info'] = stats.get('company_info', 0) + 1
                    else:
                        stats['failed'] += 1
                        success = False
            
            # 更新行业信息
            if args.data_type in ['all', 'industry']:
                if update_industry_info(code, industry_service, basic_info):
                    stats['industry'] += 1
                else:
                    stats['failed'] += 1
                    success = False
            
            # 更新股东信息
            if args.data_type in ['all', 'shareholders']:
                if update_shareholders(code, shareholder_service):
                    stats['shareholders'] += 1
                else:
                    stats['failed'] += 1
                    success = False
                time.sleep(args.delay)
            
            # 更新市值信息
            # 如果是批量更新且已批量更新了市值信息，则跳过
            if args.data_type in ['all', 'market_value']:
                # 批量更新时，市值信息已更新，这里跳过
                if not is_batch_update:
                    if update_market_value(code, market_value_service):
                        stats['market_value'] += 1
                    else:
                        stats['failed'] += 1
                        success = False
                    time.sleep(args.delay)  # 添加延迟避免API限流
            
            # 更新财务数据
            if args.data_type in ['all', 'financial']:
                # 如果是批量更新且已筛选过股票，只更新筛选出的股票
                if is_batch_update and stocks_to_update_financial is not None:
                    if code not in stocks_to_update_financial:
                        logger.debug(f"股票 {code} 已包含上一个报告期数据，跳过更新")
                    else:
                        if update_financial_data(code, financial_service):
                            stats['financial'] += 1
                        else:
                            stats['failed'] += 1
                            success = False
                        time.sleep(args.delay)
                else:
                    # 单个股票更新或未筛选的情况，正常更新
                    if update_financial_data(code, financial_service):
                        stats['financial'] += 1
                    else:
                        stats['failed'] += 1
                        success = False
                    time.sleep(args.delay)
            
            # 批量处理时的进度提示
            if i % args.batch_size == 0:
                logger.info(f"已处理 {i}/{len(stocks)} 只股票")
        
        # 输出统计信息
        logger.info("=" * 50)
        logger.info("数据更新完成！")
        if 'company_info' in stats:
            logger.info(f"公司信息: {stats['company_info']} 只股票")
        logger.info(f"行业信息: {stats['industry']} 只股票")
        logger.info(f"股东信息: {stats['shareholders']} 只股票")
        logger.info(f"市值信息: {stats['market_value']} 只股票")
        logger.info(f"财务数据: {stats['financial']} 只股票")
        logger.info(f"失败: {stats['failed']} 次")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

