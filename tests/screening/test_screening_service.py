"""
选股服务测试

测试选股服务的基本功能。
"""
import unittest
from unittest.mock import Mock, patch

from src.screening.screening_service import ScreeningService
from src.screening.conditions.basic_conditions import CodeListCondition
from src.screening.combinators import AndCombinator


class TestScreeningService(unittest.TestCase):
    """测试选股服务"""
    
    def setUp(self):
        """设置测试环境"""
        self.service = ScreeningService()
    
    def test_get_stock_codes(self):
        """测试获取股票代码列表"""
        # 创建简单的条件
        condition = CodeListCondition(codes=['000001', '000002'])
        
        # 测试获取代码列表
        result = self.service.get_stock_codes(
            condition,
            initial_codes=['000001', '000002', '000003', '000004']
        )
        
        self.assertEqual(set(result), {'000001', '000002'})
    
    def test_count_stocks(self):
        """测试统计股票数量"""
        # 创建简单的条件
        condition = CodeListCondition(codes=['000001', '000002'])
        
        # 测试统计数量
        count = self.service.count_stocks(
            condition,
            initial_codes=['000001', '000002', '000003', '000004']
        )
        
        self.assertEqual(count, 2)
    
    def test_clear_cache(self):
        """测试清除缓存"""
        # 先获取一次，触发缓存
        condition = CodeListCondition(codes=['000001'])
        self.service.get_stock_codes(condition)
        
        # 清除缓存
        self.service.clear_cache()
        
        # 验证缓存已清除
        self.assertIsNone(self.service._all_stocks_cache)


if __name__ == '__main__':
    unittest.main()
