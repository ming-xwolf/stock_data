#!/bin/bash

# Dolt Git 功能测试脚本
# 演示 Dolt 的版本控制功能，类似于 Git

set -e

echo "=========================================="
echo "Dolt Git 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试数据库名称
DB_NAME="test_stock_db"

echo -e "${BLUE}步骤 1: 创建测试数据库${NC}"
docker exec stock_data_dolt dolt sql -q "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME;"
echo "✓ 数据库创建成功"
echo ""

echo -e "${BLUE}步骤 2: 初始化 Dolt 仓库${NC}"
if docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt init" 2>&1 | grep -q "already been initialized"; then
    echo "✓ Dolt 仓库已存在，跳过初始化"
else
    echo "✓ Dolt 仓库初始化成功"
fi

echo -e "${BLUE}步骤 2.1: 配置用户信息${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt config --local --add user.name 'Test User'"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt config --local --add user.email 'test@example.com'"
echo "✓ 用户信息配置成功"
echo ""

echo -e "${BLUE}步骤 3: 创建股票信息表${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2),
    volume BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"
echo "✓ 表创建成功"
echo ""

echo -e "${BLUE}步骤 4: 添加初始数据${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; DELETE FROM stocks WHERE code IN ('000001', '000002', '600000', '600519', '000858', '002415');" 2>/dev/null || true
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; INSERT INTO stocks (code, name, price, volume) VALUES
('000001', '平安银行', 12.50, 1000000),
('000002', '万科A', 18.30, 2000000),
('600000', '浦发银行', 8.90, 1500000);"
echo "✓ 初始数据插入成功"
echo ""

echo -e "${BLUE}步骤 5: 查看当前数据${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; SELECT * FROM stocks;"
echo ""

echo -e "${BLUE}步骤 6: 查看工作区状态（类似 git status）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt status"
echo ""

echo -e "${BLUE}步骤 7: 添加更改到暂存区（类似 git add）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt add stocks"
echo "✓ 表已添加到暂存区"
echo ""

echo -e "${BLUE}步骤 8: 提交更改（类似 git commit）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt commit -m '初始提交: 添加3只股票数据'"
echo "✓ 提交成功"
echo ""

echo -e "${BLUE}步骤 9: 查看提交历史（类似 git log）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt log --oneline"
echo ""

echo -e "${BLUE}步骤 10: 修改数据${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; UPDATE stocks SET price = 12.80, volume = 1200000 WHERE code = '000001';"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; INSERT INTO stocks (code, name, price, volume) VALUES ('600519', '贵州茅台', 1850.00, 500000);"
echo "✓ 数据已修改"
echo ""

echo -e "${BLUE}步骤 11: 查看数据差异（类似 git diff）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt diff stocks"
echo ""

echo -e "${BLUE}步骤 12: 提交第二次更改${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt add stocks"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt commit -m '更新平安银行价格，添加贵州茅台'"
echo "✓ 第二次提交成功"
echo ""

echo -e "${BLUE}步骤 13: 查看详细提交历史${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt log"
echo ""

echo -e "${BLUE}步骤 14: 创建分支（类似 git branch）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt branch feature-add-more-stocks"
echo "✓ 分支创建成功"
echo ""

echo -e "${BLUE}步骤 15: 切换到新分支（类似 git checkout）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt checkout feature-add-more-stocks"
echo "✓ 已切换到 feature-add-more-stocks 分支"
echo ""

echo -e "${BLUE}步骤 16: 在新分支上添加数据${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; INSERT INTO stocks (code, name, price, volume) VALUES
('000858', '五粮液', 145.50, 800000),
('002415', '海康威视', 32.40, 3000000);"
echo "✓ 新数据已添加"
echo ""

echo -e "${BLUE}步骤 17: 提交分支更改${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt add stocks"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt commit -m '添加五粮液和海康威视'"
echo "✓ 分支提交成功"
echo ""

echo -e "${BLUE}步骤 18: 查看所有分支（类似 git branch -a）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt branch -a"
echo ""

echo -e "${BLUE}步骤 19: 切换回主分支${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt checkout main"
echo "✓ 已切换回 main 分支"
echo ""

echo -e "${BLUE}步骤 20: 查看主分支的数据（应该没有新添加的股票）${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; SELECT code, name FROM stocks ORDER BY code;"
echo ""

echo -e "${BLUE}步骤 21: 合并分支（类似 git merge）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt merge feature-add-more-stocks -m '合并feature分支'"
echo "✓ 分支合并成功"
echo ""

echo -e "${BLUE}步骤 22: 查看合并后的数据${NC}"
docker exec stock_data_dolt dolt sql -q "USE $DB_NAME; SELECT code, name, price FROM stocks ORDER BY code;"
echo ""

echo -e "${BLUE}步骤 23: 查看提交图（类似 git log --graph）${NC}"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt log --oneline --graph"
echo ""

echo -e "${BLUE}步骤 24: 查看特定提交的详细信息${NC}"
COMMIT_HASH=$(docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt log --oneline | head -n 1 | awk '{print \$1}'")
echo "查看提交: $COMMIT_HASH"
docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt diff $COMMIT_HASH^..$COMMIT_HASH stocks" 2>/dev/null || docker exec stock_data_dolt bash -c "cd /var/lib/dolt/$DB_NAME && dolt log -n 1"
echo ""

echo -e "${GREEN}=========================================="
echo "测试完成！"
echo "==========================================${NC}"
echo ""
echo "Dolt 的 Git 功能演示完成，包括："
echo "  ✓ 初始化仓库"
echo "  ✓ 添加和提交更改"
echo "  ✓ 查看提交历史"
echo "  ✓ 查看数据差异"
echo "  ✓ 创建和切换分支"
echo "  ✓ 合并分支"
echo "  ✓ 查看提交详情"
echo ""
echo "测试数据库: $DB_NAME"
echo "数据位置: /var/lib/dolt/$DB_NAME"
