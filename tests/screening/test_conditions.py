"""
选股条件测试

测试各种选股条件的基本功能。
"""
import unittest
from typing import List

from src.screening.conditions.base import BaseCondition
from src.screening.conditions.basic_conditions import (
    MarketCondition,
    CodeListCondition,
)


class TestBaseCondition(unittest.TestCase):
    """测试基础条件类"""
    
    def test_get_name(self):
        """测试获取条件名称"""
        condition = MarketCondition(market='SH')
        self.assertEqual(condition.get_name(), 'MarketCondition')
    
    def test_get_description(self):
        """测试获取条件描述"""
        condition = MarketCondition(market='SH')
        desc = condition.get_description()
        self.assertIn('MarketCondition', desc)
        self.assertIn('SH', str(desc))


class TestCodeListCondition(unittest.TestCase):
    """测试股票代码列表条件"""
    
    def test_filter_include(self):
        """测试包含模式"""
        condition = CodeListCondition(codes=['000001', '000002', '000003'])
        result = condition.filter(['000001', '000002', '000004', '000005'])
        self.assertEqual(set(result), {'000001', '000002'})
    
    def test_filter_exclude(self):
        """测试排除模式"""
        condition = CodeListCondition(codes=['000001', '000002'], exclude=True)
        result = condition.filter(['000001', '000002', '000004', '000005'])
        self.assertEqual(set(result), {'000004', '000005'})
    
    def test_filter_empty_input(self):
        """测试空输入"""
        condition = CodeListCondition(codes=['000001', '000002'])
        result = condition.filter([])
        self.assertEqual(result, [])
    
    def test_filter_no_codes(self):
        """测试无代码列表"""
        condition = CodeListCondition(codes=[])
        result = condition.filter(['000001', '000002'])
        self.assertEqual(result, [])


class TestCombinators(unittest.TestCase):
    """测试组合器"""
    
    def test_and_combinator(self):
        """测试AND组合器"""
        from src.screening.combinators import AndCombinator
        
        # 创建两个条件：包含000001和000002
        condition1 = CodeListCondition(codes=['000001', '000002', '000003'])
        condition2 = CodeListCondition(codes=['000002', '000003', '000004'])
        
        # AND组合：应该只返回000002和000003
        and_condition = AndCombinator([condition1, condition2])
        result = and_condition.filter(['000001', '000002', '000003', '000004', '000005'])
        self.assertEqual(set(result), {'000002', '000003'})
    
    def test_or_combinator(self):
        """测试OR组合器"""
        from src.screening.combinators import OrCombinator
        
        # 创建两个条件
        condition1 = CodeListCondition(codes=['000001', '000002'])
        condition2 = CodeListCondition(codes=['000003', '000004'])
        
        # OR组合：应该返回所有代码
        or_condition = OrCombinator([condition1, condition2])
        result = or_condition.filter(['000001', '000002', '000003', '000004', '000005'])
        self.assertEqual(set(result), {'000001', '000002', '000003', '000004'})


if __name__ == '__main__':
    unittest.main()
