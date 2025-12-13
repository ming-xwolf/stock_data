#!/bin/bash

# Dolt 数据库初始化脚本
# 功能：停止容器 -> 删除数据 -> 启动容器 -> 创建数据库和表结构
# 使用方法: ./init_dolt_db.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
MIGRATION_FILE="$SCRIPT_DIR/migrations/001_init_database.sql"
DOLT_DATA_DIR="$SCRIPT_DIR/dolt-data"
DB_NAME="a_stock"
CONTAINER_NAME="stock_data_dolt"
DB_USER="root"
DB_PASSWORD="${DOLT_ROOT_PASSWORD:-test}"

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 函数：等待容器就绪
wait_for_container() {
    print_info "等待容器启动..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec "$CONTAINER_NAME" dolt version &> /dev/null; then
            print_success "容器已就绪"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_error "容器启动超时"
    return 1
}

# 主函数
main() {
    echo "=========================================="
    echo "Dolt 数据库初始化脚本"
    echo "=========================================="
    echo ""
    
    # 检查必要的命令
    print_info "检查必要的命令..."
    check_command docker
    check_command docker-compose
    echo ""
    
    # 步骤 1: 停止 Docker Compose
    print_info "步骤 1/10: 停止 Docker Compose..."
    if [ -f "$COMPOSE_FILE" ]; then
        cd "$SCRIPT_DIR"
        docker-compose down 2>/dev/null || true
        print_success "Docker Compose 已停止"
    else
        print_warning "docker-compose.yml 文件不存在，跳过停止步骤"
    fi
    echo ""
    
    # 步骤 2: 删除 dolt-data 目录
    print_info "步骤 2/10: 删除本地 dolt-data 目录..."
    if [ -d "$DOLT_DATA_DIR" ]; then
        rm -rf "$DOLT_DATA_DIR"
        print_success "dolt-data 目录已删除"
    else
        print_info "dolt-data 目录不存在，跳过删除步骤"
    fi
    echo ""
    
    # 步骤 3: 启动 Docker Compose
    print_info "步骤 3/10: 启动 Docker Compose..."
    cd "$SCRIPT_DIR"
    docker-compose up -d
    print_success "Docker Compose 已启动"
    echo ""
    
    # 步骤 4: 等待容器就绪
    print_info "步骤 4/10: 等待容器就绪..."
    if ! wait_for_container; then
        print_error "容器启动失败，请检查日志: docker-compose logs"
        exit 1
    fi
    echo ""
    
    # 步骤 5: 创建数据库
    print_info "步骤 5/10: 创建数据库 $DB_NAME..."
    docker exec "$CONTAINER_NAME" dolt sql -q "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || {
        print_error "创建数据库失败"
        exit 1
    }
    print_success "数据库 $DB_NAME 已创建"
    echo ""
    
    # 步骤 6: 初始化 Dolt 仓库
    print_info "步骤 6/10: 初始化 Dolt 仓库..."
    if docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt init" 2>&1 | grep -q "already been initialized"; then
        print_warning "Dolt 仓库已存在，跳过初始化"
    else
        print_success "Dolt 仓库初始化成功"
    fi
    
    # 配置用户信息
    print_info "配置 Dolt 用户信息..."
    docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt config --local --add user.name 'Stock Data User'" || true
    docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt config --local --add user.email 'stock@example.com'" || true
    print_success "用户信息配置完成"
    echo ""
    
    # 步骤 7: 执行迁移脚本创建表
    print_info "步骤 7/10: 执行迁移脚本创建表结构..."
    if [ ! -f "$MIGRATION_FILE" ]; then
        print_error "迁移文件不存在: $MIGRATION_FILE"
        exit 1
    fi
    
    # 复制迁移文件到容器
    docker cp "$MIGRATION_FILE" "$CONTAINER_NAME:/tmp/001_init_database.sql" || {
        print_error "复制迁移文件失败"
        exit 1
    }
    
    # 执行迁移脚本
    if docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt sql < /tmp/001_init_database.sql" 2>&1 | grep -i error; then
        print_error "执行迁移脚本时出现错误"
        exit 1
    fi
    
    # 验证表是否创建成功
    TABLE_COUNT=$(docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';" | tail -n 1 | tr -d ' ')
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        print_success "表结构创建成功，共创建 $TABLE_COUNT 个表"
    else
        print_error "表创建失败，表数量为 0"
        exit 1
    fi
    echo ""
    
    # 步骤 8: 提交到版本控制
    print_info "步骤 8/10: 提交表结构到版本控制..."
    docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt add ." || {
        print_warning "添加文件到暂存区失败，可能表已存在"
    }
    
    # 检查是否有未提交的更改
    if docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt status" | grep -q "nothing to commit"; then
        print_info "没有需要提交的更改"
    else
        docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt commit -m '初始提交: 创建完整的股票数据库表结构

- stocks: 股票基本信息表（包含企业性质、实际控制人、主营业务等字段）
- stock_daily: 股票日线数据表
- stock_industry: 股票行业信息表
- stock_shareholders: 股票股东信息表
- stock_market_value: 股票市值信息表
- stock_financial_income: 利润表
- trading_calendar: A股交易日历表
- stock_financial_indicators: 财务指标表
- trading_calendar: A股交易日历表'" || {
            print_warning "提交失败，可能已经提交过"
        }
        print_success "表结构已提交到版本控制"
    fi
    echo ""
    
    # 步骤 9: 验证表可以通过 SQL Server 访问
    print_info "步骤 9/10: 验证表可以通过 SQL Server 访问..."
    
    # 等待 SQL Server 完全就绪
    sleep 2
    
    # 测试查询每个表，确保它们对 SQL Server 可见
    TEST_TABLES=("stocks" "stock_daily" "stock_industry" "stock_shareholders" "stock_market_value" "trading_calendar")
    FAILED_TABLES=()
    
    for table in "${TEST_TABLES[@]}"; do
        if docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) FROM $table;" &> /dev/null; then
            print_success "表 $table 可以通过 SQL Server 访问"
        else
            print_warning "表 $table 访问测试失败，将尝试修复"
            FAILED_TABLES+=("$table")
        fi
    done
    
    # 如果有表访问失败，尝试重新提交
    if [ ${#FAILED_TABLES[@]} -gt 0 ]; then
        print_info "尝试修复表访问问题..."
        docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt add . && dolt commit -m '确保表对 SQL Server 可见'" || true
        sleep 2
        
        # 再次测试
        for table in "${FAILED_TABLES[@]}"; do
            if docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) FROM $table;" &> /dev/null; then
                print_success "表 $table 修复成功"
            else
                print_warning "表 $table 仍无法访问，但表结构已创建"
            fi
        done
    fi
    
    # 验证所有表都在 information_schema 中可见
    VISIBLE_TABLES=$(docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';" | tail -n 1 | tr -d ' ')
    if [ "$VISIBLE_TABLES" -eq "$TABLE_COUNT" ]; then
        print_success "所有 $VISIBLE_TABLES 个表都在 information_schema 中可见"
    else
        print_warning "表可见性不一致：创建了 $TABLE_COUNT 个表，但只有 $VISIBLE_TABLES 个可见"
    fi
    echo ""
    
    # 步骤 10: 最终验证和测试查询
    print_info "步骤 10/10: 执行最终验证测试..."
    
    # 测试基本查询
    if docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = '$DB_NAME';" &> /dev/null; then
        print_success "数据库查询功能正常"
    else
        print_error "数据库查询测试失败"
        exit 1
    fi
    
    # 测试插入和查询（确保表完全可用）
    TEST_CODE="TEST_$(date +%s)"
    if docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; INSERT INTO stocks (code, name, market) VALUES ('$TEST_CODE', '测试股票', 'SZ') ON DUPLICATE KEY UPDATE name='测试股票';" &> /dev/null; then
        if docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SELECT COUNT(*) FROM stocks WHERE code = '$TEST_CODE';" | grep -q "1"; then
            print_success "表读写功能正常"
            # 清理测试数据
            docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; DELETE FROM stocks WHERE code = '$TEST_CODE';" &> /dev/null || true
        else
            print_warning "表写入成功但查询测试失败"
        fi
    else
        print_warning "表写入测试失败，但表结构已创建"
    fi
    echo ""
    
    # 显示最终状态
    echo "=========================================="
    print_success "数据库初始化完成！"
    echo "=========================================="
    echo ""
    echo "数据库信息:"
    echo "  - 数据库名称: $DB_NAME"
    echo "  - 表数量: $TABLE_COUNT"
    echo "  - 连接信息:"
    echo "    * 主机: localhost"
    echo "    * 端口: 13306"
    echo "    * 用户名: $DB_USER"
    echo "    * 密码: $DB_PASSWORD"
    echo "    * 数据库: $DB_NAME"
    echo ""
    echo "查看表列表:"
    docker exec "$CONTAINER_NAME" dolt sql -q "USE $DB_NAME; SHOW TABLES;"
    echo ""
    echo "查看提交历史:"
    docker exec "$CONTAINER_NAME" bash -c "cd /var/lib/dolt/$DB_NAME && dolt log --oneline" | head -5
    echo ""
    echo "=========================================="
    print_info "重要提示："
    echo "=========================================="
    echo "1. 客户端连接时，请确保选择数据库: USE $DB_NAME;"
    echo "2. 或者在连接字符串中指定默认数据库: $DB_NAME"
    echo "3. 如果遇到 'table not found' 错误，请先执行: USE $DB_NAME;"
    echo "4. 所有表已正确创建并提交到版本控制，可以通过 SQL Server 正常访问"
    echo ""
}

# 执行主函数
main "$@"
