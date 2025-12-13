"""
AKShare数据获取模块

使用AKShare API获取A股股票列表和基本信息。
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from functools import lru_cache

import akshare as ak
from .cache_manager import (
    cached_api_call, _cache_stock_basic_info, _cache_stock_list,
    _cache_stock_controller, _cache_stock_shareholders, 
    _cache_stock_market_value, _cache_stock_financial,
    clear_all_caches as clear_caches, get_cache_stats
)

logger = logging.getLogger(__name__)


class AKShareClient:
    """AKShare客户端类"""
    
    @staticmethod
    def _get_market_from_code(code: str) -> str:
        """
        根据股票代码判断市场
        
        Args:
            code: 股票代码（6位数字）
            
        Returns:
            市场代码：
            - 0、3开头 -> SZ（深圳证券交易所）
            - 6开头 -> SH（上海证券交易所）
            - 8、92开头 -> BJ（北京证券交易所）
            - 其他 -> SH（默认）
        """
        if code.startswith('6'):
            return 'SH'
        elif code.startswith(('0', '3')):
            return 'SZ'
        elif code.startswith(('8', '92')):
            return 'BJ'
        else:
            # 如果无法判断，默认使用上海
            return 'SH' if len(code) == 6 and code[0] == '6' else 'SZ'
    
    @staticmethod
    def _convert_code_to_symbol(code: str) -> str:
        """
        将股票代码转换为带市场标识的格式
        
        Args:
            code: 股票代码（6位数字）
            
        Returns:
            带市场标识的代码：
            - 0、3开头 -> SZ（深圳证券交易所）
            - 6开头 -> SH（上海证券交易所）
            - 8、92开头 -> BJ（北京证券交易所）
            - 其他 -> SH（默认）
        """
        market = AKShareClient._get_market_from_code(code)
        return f'{market}{code}'
    
    @staticmethod
    @cached_api_call(_cache_stock_basic_info, ttl=86400)  # 24小时缓存
    def get_stock_basic_info(code: str) -> Optional[Dict[str, any]]:
        """
        一次性获取股票的所有基本信息（避免重复调用API）
        
        Args:
            code: 股票代码
            
        Returns:
            包含所有基本信息的字典：
            - list_date: 上市日期
            - company_type: 企业性质
            - actual_controller: 实际控制人
            - main_business: 主营产品
            - industry_name: 行业名称
            - concept: 概念板块
            - area: 地区
        """
        basic_info = {}
        
        # 方法1: 尝试使用 stock_individual_info_em (东方财富)
        try:
            stock_info = ak.stock_individual_info_em(symbol=code)
            
            if stock_info is not None and not stock_info.empty:
                # 提取上市日期
                list_date_row = stock_info[stock_info['item'] == '上市时间']
                if not list_date_row.empty:
                    date_str = str(list_date_row.iloc[0]['value'])
                    # 格式: 19910403 -> 1991-04-03
                    if len(date_str) == 8 and date_str.isdigit():
                        basic_info['list_date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                
                # 提取行业信息
                industry_row = stock_info[stock_info['item'] == '行业']
                if not industry_row.empty:
                    basic_info['industry_name'] = industry_row.iloc[0]['value']
                
                # 提取企业性质
                company_type_row = stock_info[stock_info['item'].str.contains('企业性质|所有制|公司性质', na=False)]
                if not company_type_row.empty:
                    basic_info['company_type'] = company_type_row.iloc[0]['value']
                
                # 提取实际控制人
                controller_row = stock_info[stock_info['item'].str.contains('实际控制人|控股股东|控制人', na=False)]
                if not controller_row.empty:
                    basic_info['actual_controller'] = controller_row.iloc[0]['value']
                
                # 提取主营产品/主营业务
                business_row = stock_info[stock_info['item'].str.contains('主营业务|主营产品|经营范围', na=False)]
                if not business_row.empty:
                    basic_info['main_business'] = business_row.iloc[0]['value']
                
                # 提取概念
                concept_row = stock_info[stock_info['item'] == '概念板块']
                if not concept_row.empty:
                    basic_info['concept'] = concept_row.iloc[0]['value']
                
                # 提取地区
                area_row = stock_info[stock_info['item'] == '所属地域']
                if not area_row.empty:
                    basic_info['area'] = area_row.iloc[0]['value']
                
                logger.debug(f"成功使用 stock_individual_info_em 获取股票 {code} 基本信息")
            
                logger.debug(f"成功使用 stock_individual_info_em 获取股票 {code} 基本信息")
        except Exception as e:
            logger.debug(f"使用 stock_individual_info_em 获取股票 {code} 基本信息失败: {e}")
        
        # 方法2: 如果方法1失败或数据不完整，使用 stock_individual_basic_info_xq (雪球) 作为备用
        try:
            # 转换代码格式：000001 -> SZ000001, 600519 -> SH600519, 920139 -> BJ920139
            symbol_code = AKShareClient._convert_code_to_symbol(code)
            basic_info_xq = ak.stock_individual_basic_info_xq(symbol=symbol_code)
            
            if basic_info_xq is not None and not basic_info_xq.empty:
                # 补充缺失的上市日期
                if 'list_date' not in basic_info:
                    established_row = basic_info_xq[basic_info_xq['item'] == 'established_date']
                    if not established_row.empty:
                        timestamp = established_row.iloc[0]['value']
                        if timestamp and str(timestamp) != 'None' and str(timestamp) != 'nan':
                            try:
                                from datetime import datetime
                                dt = datetime.fromtimestamp(int(timestamp) / 1000)
                                basic_info['list_date'] = dt.strftime('%Y-%m-%d')
                            except:
                                pass
                
                # 补充缺失的企业性质（classi_name字段）
                if 'company_type' not in basic_info:
                    classi_row = basic_info_xq[basic_info_xq['item'] == 'classi_name']
                    if not classi_row.empty:
                        value = classi_row.iloc[0]['value']
                        if value and str(value) != 'None' and str(value) != 'nan' and str(value).strip():
                            basic_info['company_type'] = str(value).strip()
                    
                    # 如果classi_name不存在，尝试其他可能的字段名
                    if 'company_type' not in basic_info:
                        # 尝试查找所有包含"性质"、"类型"、"分类"等关键词的字段
                        possible_items = basic_info_xq[
                            basic_info_xq['item'].str.contains('性质|类型|分类|所有制', na=False, case=False)
                        ]
                        if not possible_items.empty:
                            value = possible_items.iloc[0]['value']
                            if value and str(value) != 'None' and str(value) != 'nan' and str(value).strip():
                                basic_info['company_type'] = str(value).strip()
                
                # 补充缺失的实际控制人（如果actual_controller字段有值）
                if 'actual_controller' not in basic_info:
                    controller_row = basic_info_xq[basic_info_xq['item'] == 'actual_controller']
                    if not controller_row.empty:
                        value = controller_row.iloc[0]['value']
                        if value and str(value) != 'None' and str(value) != 'nan' and str(value).strip():
                            # 提取实际控制人名称（去除持股比例）
                            controller_str = str(value).strip()
                            # 格式可能是: "贵州省人民政府国有资产监督管理委员会 (48.91%)"
                            if '(' in controller_str:
                                controller_str = controller_str.split('(')[0].strip()
                            basic_info['actual_controller'] = controller_str
                
                # 补充缺失的主营业务
                if 'main_business' not in basic_info:
                    main_business_row = basic_info_xq[basic_info_xq['item'] == 'main_operation_business']
                    if not main_business_row.empty:
                        value = main_business_row.iloc[0]['value']
                        if value and str(value) != 'None' and str(value) != 'nan':
                            basic_info['main_business'] = str(value)
                
                # 补充公司简介（如果没有主营业务）
                if 'main_business' not in basic_info:
                    intro_row = basic_info_xq[basic_info_xq['item'] == 'org_cn_introduction']
                    if not intro_row.empty:
                        value = intro_row.iloc[0]['value']
                        if value and str(value) != 'None' and str(value) != 'nan':
                            basic_info['main_business'] = str(value)
                
                logger.debug(f"成功使用 stock_individual_basic_info_xq 补充股票 {code} 基本信息")
        except Exception as e:
            logger.debug(f"使用 stock_individual_basic_info_xq 获取股票 {code} 基本信息失败: {e}")
        
        # 方法3: 如果企业性质仍然缺失，尝试从控制人信息推断（仅对92开头的股票）
        if 'company_type' not in basic_info and code.startswith('92'):
            try:
                controller_info = AKShareClient.get_stock_controller_info(code)
                if controller_info:
                    actual_controller = controller_info.get('actual_controller')
                    if actual_controller:
                        # 根据实际控制人推断企业性质
                        controller_str = str(actual_controller).strip()
                        if '国务院' in controller_str or '国资委' in controller_str or '国有资产' in controller_str:
                            basic_info['company_type'] = '央企国资控股'
                        elif '省' in controller_str and ('国资委' in controller_str or '国有资产' in controller_str):
                            basic_info['company_type'] = '地方国资控股'
                        elif '市' in controller_str and ('国资委' in controller_str or '国有资产' in controller_str):
                            basic_info['company_type'] = '地方国资控股'
                        elif '人民政府' in controller_str:
                            basic_info['company_type'] = '地方国资控股'
                        elif '集体' in controller_str:
                            basic_info['company_type'] = '集体企业'
                        elif '外资' in controller_str or '外商' in controller_str:
                            basic_info['company_type'] = '外资企业'
                        else:
                            # 默认为民企
                            basic_info['company_type'] = '民企'
                        logger.debug(f"从控制人信息推断股票 {code} 企业性质: {basic_info['company_type']}")
            except Exception as e:
                logger.debug(f"从控制人信息推断股票 {code} 企业性质失败: {e}")
        
        return basic_info if basic_info else None
    
    @staticmethod
    @cached_api_call(_cache_stock_list, ttl=3600)  # 1小时缓存
    def get_stock_list() -> List[Dict[str, any]]:
        """
        获取A股股票列表
        
        Returns:
            股票列表，每个元素包含股票代码、名称等信息
        """
        try:
            logger.info("开始获取A股股票列表...")
            
            # 获取A股股票列表
            stock_info = ak.stock_info_a_code_name()
            
            if stock_info is None or stock_info.empty:
                logger.warning("未获取到股票数据")
                return []
            
            logger.info(f"成功获取 {len(stock_info)} 只股票")
            
            # 转换为字典列表
            stocks = []
            for _, row in stock_info.iterrows():
                # 处理不同的列名可能（code/code, name/name）
                code = str(row.get('code', row.get('股票代码', ''))).strip()
                name = str(row.get('name', row.get('股票名称', ''))).strip()
                
                if not code or not name:
                    continue
                
                # 解析市场代码（SH/SZ/BJ）
                # 6开头是上海，0/3开头是深圳，8/92开头是北京
                market = AKShareClient._get_market_from_code(code)
                
                stocks.append({
                    'code': code,
                    'name': name,
                    'market': market,
                })
            
            logger.info(f"成功解析 {len(stocks)} 只股票")
            return stocks
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_stock_list_date(code: str, basic_info: Optional[Dict[str, any]] = None) -> Optional[str]:
        """
        获取股票的上市日期
        
        Args:
            code: 股票代码
            basic_info: 可选，如果提供则从中提取，避免重复调用API
            
        Returns:
            上市日期字符串（YYYY-MM-DD格式），如果获取失败返回None
        """
        if basic_info and 'list_date' in basic_info:
            return basic_info['list_date']
        
        # 如果没有提供basic_info，则调用统一方法
        basic_info = AKShareClient.get_stock_basic_info(code)
        return basic_info.get('list_date') if basic_info else None
    
    @staticmethod
    def enrich_stock_info(stocks: List[Dict[str, any]], 
                          include_list_date: bool = True) -> List[Dict[str, any]]:
        """
        丰富股票信息，添加上市日期等
        
        Args:
            stocks: 股票列表
            include_list_date: 是否包含上市日期
            
        Returns:
            丰富后的股票列表
        """
        if not include_list_date:
            return stocks
        
        logger.info("开始获取股票上市日期...")
        enriched_stocks = []
        
        for i, stock in enumerate(stocks, 1):
            code = stock['code']
            if i % 100 == 0:
                logger.info(f"已处理 {i}/{len(stocks)} 只股票")
            
            # 使用统一方法获取基本信息（包含上市日期）
            basic_info = AKShareClient.get_stock_basic_info(code)
            if basic_info:
                stock['list_date'] = basic_info.get('list_date')
            
            enriched_stocks.append(stock)
        
        logger.info("股票信息丰富完成")
        return enriched_stocks
    
    @staticmethod
    def get_stock_company_info(code: str, basic_info: Optional[Dict[str, any]] = None) -> Optional[Dict[str, any]]:
        """
        获取股票公司信息（企业性质、实际控制人、主营产品等）
        
        Args:
            code: 股票代码
            basic_info: 可选，如果提供则从中提取，避免重复调用API
            
        Returns:
            公司信息字典，包含企业性质、实际控制人、主营产品等
        """
        if basic_info is None:
            basic_info = AKShareClient.get_stock_basic_info(code)
        
        if not basic_info:
            return None
        
        # 从基本信息中提取公司相关信息
        company_info = {}
        if 'company_type' in basic_info:
            company_info['company_type'] = basic_info['company_type']
        if 'actual_controller' in basic_info:
            company_info['actual_controller'] = basic_info['actual_controller']
        if 'main_business' in basic_info:
            company_info['main_business'] = basic_info['main_business']
        
        return company_info if company_info else None
    
    @staticmethod
    def get_stock_industry_info(code: str, basic_info: Optional[Dict[str, any]] = None) -> Optional[Dict[str, any]]:
        """
        获取股票行业信息
        
        Args:
            code: 股票代码
            basic_info: 可选，如果提供则从中提取，避免重复调用API
            
        Returns:
            行业信息字典，包含行业名称、行业代码、概念、地区等
        """
        if basic_info is None:
            basic_info = AKShareClient.get_stock_basic_info(code)
        
        if not basic_info:
            return None
        
        # 从基本信息中提取行业相关信息
        industry_info = {}
        if 'industry_name' in basic_info:
            industry_info['industry_name'] = basic_info['industry_name']
        if 'concept' in basic_info:
            industry_info['concept'] = basic_info['concept']
        if 'area' in basic_info:
            industry_info['area'] = basic_info['area']
        
        return industry_info if industry_info else None
    
    @staticmethod
    @cached_api_call(_cache_stock_shareholders, ttl=86400)  # 24小时缓存
    def get_stock_shareholders(code: str, period: str = "latest") -> List[Dict[str, any]]:
        """
        获取股票股东信息
        
        Args:
            code: 股票代码
            period: 报告期，'latest'表示最新报告期
            
        Returns:
            股东信息列表
        """
        try:
            # 获取主要股东信息（使用stock_main_stock_holder）
            shareholders_df = ak.stock_main_stock_holder(stock=code)
            
            if shareholders_df is None or shareholders_df.empty:
                return []
            
            shareholders = []
            for _, row in shareholders_df.iterrows():
                # 使用实际的列名
                shareholder_name = str(row.get('股东名称', '')).strip()
                holding_ratio = AKShareClient._parse_float(row.get('持股比例', 0))
                holding_amount = AKShareClient._parse_int(row.get('持股数量', 0))
                report_date = AKShareClient._parse_date(row.get('截至日期', row.get('公告日期', '')))
                
                if not shareholder_name or shareholder_name == 'nan':
                    continue
                
                shareholder = {
                    'code': code,
                    'shareholder_name': shareholder_name,
                    'holding_ratio': holding_ratio,
                    'holding_amount': holding_amount,
                    'change_amount': None,  # stock_main_stock_holder不提供变化数据
                    'change_ratio': None,
                    'report_date': report_date,
                }
                
                # 判断股东类型
                name = shareholder['shareholder_name']
                if '银行' in name or '基金' in name or '保险' in name or '投资' in name:
                    shareholder['shareholder_type'] = '机构'
                elif '公司' in name or '集团' in name or '有限' in name:
                    shareholder['shareholder_type'] = '法人'
                else:
                    shareholder['shareholder_type'] = '个人'
                
                shareholders.append(shareholder)
            
            return shareholders
            
        except Exception as e:
            logger.debug(f"获取股票 {code} 股东信息失败: {e}")
            return []
    
    
    @staticmethod
    @cached_api_call(_cache_stock_market_value, ttl=300)  # 5分钟缓存（市值数据变化较快）
    def get_stock_market_value(code: str, spot_data: Optional[any] = None) -> Optional[Dict[str, any]]:
        """
        获取股票市值信息
        
        使用 stock_individual_spot_xq (雪球) 获取单只股票的市值信息
        
        Args:
            code: 股票代码
            spot_data: 已废弃，保留以兼容旧代码
            
        Returns:
            市值信息字典
        """
        try:
            # 转换代码格式：000001 -> SZ000001, 600519 -> SH600519, 920139 -> BJ920139
            symbol_code = AKShareClient._convert_code_to_symbol(code)
            spot_xq = ak.stock_individual_spot_xq(symbol=symbol_code)
            
            if spot_xq is not None and not spot_xq.empty:
                # 转换为字典格式便于查找
                spot_dict = {}
                for _, row in spot_xq.iterrows():
                    item = str(row.get('item', ''))
                    value = row.get('value', '')
                    spot_dict[item] = value
                
                # 提取市值信息
                # 总市值: "资产净值/总市值"
                total_market_cap = AKShareClient._parse_float(spot_dict.get('资产净值/总市值', spot_dict.get('总市值', 0)))
                # 流通市值: "流通值"
                circulating_market_cap = AKShareClient._parse_float(spot_dict.get('流通值', spot_dict.get('流通市值', 0)))
                # 总股本: "基金份额/总股本"
                total_shares = AKShareClient._parse_int(spot_dict.get('基金份额/总股本', spot_dict.get('总股本', 0)))
                # 流通股: "流通股"
                circulating_shares = AKShareClient._parse_int(spot_dict.get('流通股', 0))
                # 最新价: "最新" 或 "现价"
                price = AKShareClient._parse_float(spot_dict.get('最新', spot_dict.get('现价', spot_dict.get('最新价', 0))))
                
                if total_market_cap or circulating_market_cap:
                    market_value = {
                        'code': code,
                        'total_market_cap': total_market_cap,
                        'circulating_market_cap': circulating_market_cap,
                        'price': price,
                        'total_shares': total_shares,
                        'circulating_shares': circulating_shares,
                    }
                    
                    logger.debug(f"成功使用 stock_individual_spot_xq 获取股票 {code} 市值信息")
                    return market_value
        except Exception as e:
            logger.debug(f"使用 stock_individual_spot_xq 获取股票 {code} 市值信息失败: {e}")
        
        return None
    
    @staticmethod
    @cached_api_call(_cache_stock_market_value, ttl=300)  # 5分钟缓存
    def get_all_market_value() -> Optional[List[Dict[str, any]]]:
        """
        批量获取所有A股的市值信息
        
        使用 stock_zh_a_spot_em 批量获取所有A股实时行情数据
        
        Returns:
            市值信息列表，每个元素包含：
            - code: 股票代码
            - total_market_cap: 总市值
            - circulating_market_cap: 流通市值
            - price: 最新价
            - total_shares: 总股本
            - circulating_shares: 流通股
        """
        try:
            logger.info("批量获取所有A股市值信息...")
            # 尝试使用 stock_zh_a_spot_em 批量获取
            spot_df = ak.stock_zh_a_spot_em()
            
            if spot_df is not None and not spot_df.empty:
                market_values = []
                for _, row in spot_df.iterrows():
                    code = str(row.get('代码', row.get('code', ''))).strip()
                    if not code:
                        continue
                    
                    # 提取市值信息
                    total_market_cap = AKShareClient._parse_float(
                        row.get('总市值', row.get('总市值(元)', 0))
                    )
                    circulating_market_cap = AKShareClient._parse_float(
                        row.get('流通市值', row.get('流通市值(元)', 0))
                    )
                    price = AKShareClient._parse_float(
                        row.get('最新价', row.get('现价', 0))
                    )
                    total_shares = AKShareClient._parse_int(
                        row.get('总股本', row.get('总股本(股)', 0))
                    )
                    circulating_shares = AKShareClient._parse_int(
                        row.get('流通股', row.get('流通股(股)', 0))
                    )
                    
                    if total_market_cap or circulating_market_cap:
                        market_values.append({
                            'code': code,
                            'total_market_cap': total_market_cap,
                            'circulating_market_cap': circulating_market_cap,
                            'price': price,
                            'total_shares': total_shares,
                            'circulating_shares': circulating_shares,
                        })
                
                logger.info(f"成功批量获取 {len(market_values)} 只股票的市值信息")
                return market_values
        except Exception as e:
            logger.debug(f"批量获取市值信息失败，将使用单个API: {e}")
        
        return None
    
    @staticmethod
    @cached_api_call(_cache_stock_financial, ttl=86400)  # 24小时缓存
    def get_stock_financial_data(code: str, period: str = "latest") -> Optional[Dict[str, any]]:
        """
        获取股票财务数据
        
        Args:
            code: 股票代码
            period: 报告期，'latest'表示最新报告期
            
        Returns:
            财务数据字典，包含资产负债表、利润表、现金流量表数据
        """
        try:
            financial_data = {}
            
            # 获取资产负债表（需要将代码转换为SH/SZ/BJ格式）
            try:
                # 转换代码格式：000001 -> SZ000001, 600519 -> SH600519, 920139 -> BJ920139
                symbol_code = AKShareClient._convert_code_to_symbol(code)
                balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=symbol_code)
                if balance_sheet is not None and not balance_sheet.empty:
                    # 获取最新一期的数据
                    latest_row = balance_sheet.iloc[-1]
                    financial_data['balance'] = {
                        'report_date': AKShareClient._parse_date(
                            latest_row.get('REPORT_DATE', latest_row.get('报告日期', latest_row.get('日期', '')))
                        ),
                        'total_assets': AKShareClient._parse_float(
                            latest_row.get('TOTAL_ASSETS', latest_row.get('资产总计', latest_row.get('总资产', 0)))
                        ),
                        'total_liabilities': AKShareClient._parse_float(
                            latest_row.get('TOTAL_LIABILITIES', latest_row.get('负债合计', latest_row.get('总负债', 0)))
                        ),
                        'total_equity': AKShareClient._parse_float(
                            latest_row.get('TOTAL_EQUITY', latest_row.get('所有者权益合计', latest_row.get('股东权益', 0)))
                        ),
                    }
            except Exception as e:
                logger.debug(f"获取资产负债表失败: {e}")
            
            # 获取利润表
            try:
                # 转换代码格式：000001 -> SZ000001, 600519 -> SH600519, 920139 -> BJ920139
                symbol_code = AKShareClient._convert_code_to_symbol(code)
                income_statement = ak.stock_profit_sheet_by_report_em(symbol=symbol_code)
                if income_statement is not None and not income_statement.empty:
                    latest_row = income_statement.iloc[-1]
                    financial_data['income'] = {
                        'report_date': AKShareClient._parse_date(
                            latest_row.get('REPORT_DATE', latest_row.get('报告日期', latest_row.get('日期', '')))
                        ),
                        'total_revenue': AKShareClient._parse_float(
                            latest_row.get('OPERATE_INCOME', latest_row.get('营业总收入', latest_row.get('营业收入', 0)))
                        ),
                        'operating_revenue': AKShareClient._parse_float(
                            latest_row.get('OPERATE_INCOME', latest_row.get('营业收入', latest_row.get('营收', 0)))
                        ),
                        'net_profit': AKShareClient._parse_float(
                            latest_row.get('NETPROFIT', latest_row.get('净利润', latest_row.get('净利', 0)))
                        ),
                        'net_profit_attributable': AKShareClient._parse_float(
                            latest_row.get('PARENT_NETPROFIT', latest_row.get('归属于母公司所有者的净利润', latest_row.get('归母净利润', 0)))
                        ),
                    }
            except Exception as e:
                logger.debug(f"获取利润表失败: {e}")
            
            return financial_data if financial_data else None
            
        except Exception as e:
            logger.debug(f"获取股票 {code} 财务数据失败: {e}")
            return None
    
    @staticmethod
    def _parse_float(value: any) -> Optional[float]:
        """解析浮点数，将NaN转换为None"""
        import math
        
        if value is None:
            return None
        
        # 检查是否为NaN
        try:
            if isinstance(value, float) and math.isnan(value):
                return None
        except (TypeError, ValueError):
            pass
        
        try:
            if isinstance(value, str):
                # 检查字符串是否为NaN
                if value.lower() in ['nan', 'none', 'null', '']:
                    return None
                # 移除可能的单位符号
                value = value.replace('元', '').replace('万', '').replace('亿', '').strip()
                # 处理百分比
                if '%' in value:
                    value = value.replace('%', '').strip()
                result = float(value)
                # 再次检查结果是否为NaN
                if math.isnan(result):
                    return None
                return result
            result = float(value)
            # 检查结果是否为NaN
            if math.isnan(result):
                return None
            return result
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_int(value: any) -> Optional[int]:
        """解析整数"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('股', '').strip()
                return int(float(value))
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_date(value: any) -> Optional[str]:
        """解析日期"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                    try:
                        date_obj = datetime.strptime(value, fmt)
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            return str(value)
        except Exception:
            return None
    
    @staticmethod
    @cached_api_call(_cache_stock_controller, ttl=86400)  # 24小时缓存
    def get_all_controller_data():
        """
        批量获取所有股票的控制人数据
        
        Returns:
            所有股票的控制人DataFrame，包含列：证券代码、实际控制人名称、直接控制人名称等
        """
        try:
            logger.info("批量获取所有股票的控制人数据...")
            df = ak.stock_hold_control_cninfo(symbol='全部')
            if df is not None and not df.empty:
                logger.info(f"成功获取 {len(df)} 条控制人数据")
            return df
        except Exception as e:
            logger.error(f"批量获取所有股票控制人数据失败: {e}")
            return None
    
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_all_controller_data():
        """
        获取所有股票的控制人数据（缓存整个数据集）- 内部方法，保留以兼容旧代码
        
        Returns:
            所有股票的控制人DataFrame
        """
        return AKShareClient.get_all_controller_data()
    
    @staticmethod
    def parse_all_controller_data(df) -> Dict[str, Dict[str, any]]:
        """
        解析批量获取的控制人数据，转换为字典格式
        
        Args:
            df: 控制人DataFrame
            
        Returns:
            字典，key为股票代码，value为控制人信息字典
        """
        if df is None or df.empty:
            return {}
        
        controller_dict = {}
        
        # 按股票代码分组，获取每个股票的最新记录
        for code in df['证券代码'].unique():
            stock_data = df[df['证券代码'] == code]
            if stock_data.empty:
                continue
            
            # 获取最新的记录（按变动日期排序）
            latest = stock_data.sort_values('变动日期', ascending=False).iloc[0]
            
            controller_info = {
                'actual_controller': None,
                'direct_controller': None,
                'control_ratio': None,
                'control_type': None,
                'change_date': None,
            }
            
            # 提取实际控制人（如果不是"无"）
            actual_controller = latest.get('实际控制人名称', '')
            if actual_controller and str(actual_controller).strip() != '无' and str(actual_controller).strip() != 'nan':
                controller_info['actual_controller'] = str(actual_controller).strip()
            
            # 提取直接控制人
            direct_controller = latest.get('直接控制人名称', '')
            if direct_controller and str(direct_controller).strip() != 'nan':
                controller_info['direct_controller'] = str(direct_controller).strip()
            
            # 提取控股比例
            control_ratio = latest.get('控股比例', None)
            if control_ratio is not None:
                try:
                    ratio_str = str(control_ratio).replace('%', '').strip()
                    controller_info['control_ratio'] = float(ratio_str) if ratio_str else None
                except (ValueError, TypeError):
                    pass
            
            # 提取控制类型
            control_type = latest.get('控制类型', '')
            if control_type and str(control_type).strip() != 'nan':
                controller_info['control_type'] = str(control_type).strip()
            
            # 提取变动日期
            change_date = latest.get('变动日期', '')
            if change_date:
                try:
                    if isinstance(change_date, str):
                        date_obj = datetime.strptime(change_date, '%Y-%m-%d')
                        controller_info['change_date'] = date_obj.strftime('%Y-%m-%d')
                    else:
                        controller_info['change_date'] = str(change_date)
                except (ValueError, TypeError):
                    controller_info['change_date'] = str(change_date)
            
            # 只有当有实际控制人或直接控制人时才添加
            if controller_info['actual_controller'] or controller_info['direct_controller']:
                controller_dict[str(code)] = controller_info
        
        return controller_dict
    
    @staticmethod
    def get_stock_controller_info(code: str) -> Optional[Dict[str, any]]:
        """
        获取股票的实际控制人和直接控制人信息
        
        使用 stock_hold_control_cninfo API 获取控制人信息（使用缓存）
        
        Args:
            code: 股票代码
            
        Returns:
            控制人信息字典，包含：
            - actual_controller: 实际控制人名称
            - direct_controller: 直接控制人名称
            - control_ratio: 控股比例
            - control_type: 控制类型
            - change_date: 变动日期
        """
        try:
            # 从缓存获取所有股票的控制人信息
            df = AKShareClient._get_all_controller_data()
            
            if df is not None and not df.empty:
                # 查找对应股票的数据
                stock_data = df[df['证券代码'] == code]
                
                if not stock_data.empty:
                    # 获取最新的记录（按变动日期排序）
                    latest = stock_data.sort_values('变动日期', ascending=False).iloc[0]
                    
                    controller_info = {
                        'actual_controller': None,
                        'direct_controller': None,
                        'control_ratio': None,
                        'control_type': None,
                        'change_date': None,
                    }
                    
                    # 提取实际控制人（如果不是"无"）
                    actual_controller = latest.get('实际控制人名称', '')
                    if actual_controller and str(actual_controller).strip() != '无' and str(actual_controller).strip() != 'nan':
                        controller_info['actual_controller'] = str(actual_controller).strip()
                    
                    # 提取直接控制人
                    direct_controller = latest.get('直接控制人名称', '')
                    if direct_controller and str(direct_controller).strip() != 'nan':
                        controller_info['direct_controller'] = str(direct_controller).strip()
                    
                    # 提取控股比例
                    control_ratio = latest.get('控股比例', None)
                    if control_ratio is not None:
                        try:
                            # 移除百分号并转换为浮点数
                            ratio_str = str(control_ratio).replace('%', '').strip()
                            controller_info['control_ratio'] = float(ratio_str) if ratio_str else None
                        except (ValueError, TypeError):
                            pass
                    
                    # 提取控制类型
                    control_type = latest.get('控制类型', '')
                    if control_type and str(control_type).strip() != 'nan':
                        controller_info['control_type'] = str(control_type).strip()
                    
                    # 提取变动日期
                    change_date = latest.get('变动日期', '')
                    if change_date:
                        try:
                            # 尝试解析日期
                            if isinstance(change_date, str):
                                date_obj = datetime.strptime(change_date, '%Y-%m-%d')
                                controller_info['change_date'] = date_obj.strftime('%Y-%m-%d')
                            else:
                                controller_info['change_date'] = str(change_date)
                        except (ValueError, TypeError):
                            controller_info['change_date'] = str(change_date)
                    
                    logger.debug(f"成功获取股票 {code} 控制人信息")
                    return controller_info if (controller_info['actual_controller'] or controller_info['direct_controller']) else None
            
            return None
            
        except Exception as e:
            logger.debug(f"获取股票 {code} 控制人信息失败: {e}")
            return None
    
    @staticmethod
    def clear_caches():
        """清除所有缓存"""
        # 清除TimedCache缓存
        clear_caches()
        # 清除lru_cache缓存
        AKShareClient._get_all_controller_data.cache_clear()
        logger.info("所有AKShare API缓存已清除")
    
    @staticmethod
    def get_cache_stats() -> Dict[str, any]:
        """获取缓存统计信息"""
        stats = get_cache_stats()
        stats['controller_data_cache'] = AKShareClient._get_all_controller_data.cache_info()
        return stats

