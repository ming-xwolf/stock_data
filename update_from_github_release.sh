#!/bin/bash

# 从GitHub最新release更新投资数据
# 使用方法: 
#   1. 自动下载: bash update_from_github_release.sh
#   2. 使用本地tar包: bash update_from_github_release.sh --file /path/to/qlib_bin_YYYYMMDD.tar.gz
#   3. 使用本地tar包（简短参数）: bash update_from_github_release.sh -f /path/to/qlib_bin_YYYYMMDD.tar.gz
# 
# 文件名要求:
#   - 必须以 .tar.gz 结尾
#   - 建议包含日期，格式为 YYYYMMDD（例如: qlib_bin_20251211.tar.gz）
#   - 也支持 YYYY-MM-DD 格式（例如: qlib_bin_2025-12-11.tar.gz）

set -e  # 遇到错误立即退出

# 配置变量
GITHUB_REPO="chenditc/investment_data"
QLIB_DATA_DIR="$HOME/.qlib/qlib_data/cn_data"
BACKUP_DIR="$HOME/.qlib/backup"
DATA_DIR="./data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 函数：获取工作日日期（如果是周末，返回上一个周五）
# 使用Python处理日期，兼容macOS和Linux
get_workday_date() {
    python3 -c "
from datetime import datetime, timedelta
today = datetime.now()
day_of_week = today.weekday()  # 0=周一, 6=周日

if day_of_week == 5:  # 周六
    result = today - timedelta(days=1)
elif day_of_week == 6:  # 周日
    result = today - timedelta(days=2)
else:
    result = today

print(result.strftime('%Y-%m-%d'))
"
}

# 函数：获取前一个交易日
# 使用Python处理日期，兼容macOS和Linux
get_previous_trading_day() {
    local date_str=$1
    python3 -c "
from datetime import datetime, timedelta
date_obj = datetime.strptime('$date_str', '%Y-%m-%d')
day_of_week = date_obj.weekday()  # 0=周一, 6=周日

if day_of_week == 0:  # 周一，返回上一个周五（-3天）
    result = date_obj - timedelta(days=3)
elif day_of_week == 5:  # 周六，返回上一个周五（-1天）
    result = date_obj - timedelta(days=1)
elif day_of_week == 6:  # 周日，返回上一个周五（-2天）
    result = date_obj - timedelta(days=2)
else:  # 周二到周五，返回前一天（-1天）
    result = date_obj - timedelta(days=1)

print(result.strftime('%Y-%m-%d'))
"
}

# 函数：检查本地是否已有该日期的tar包
# 文件名格式：qlib_bin_YYYY-MM-DD.tar.gz（不带时间戳）
check_local_tar_exists() {
    local date_str=$1
    local expected_file="$DATA_DIR/qlib_bin_${date_str}.tar.gz"
    
    if [ -f "$expected_file" ]; then
        echo "$expected_file"
        return 0
    else
        return 1
    fi
}

# 函数：检查远程release是否存在
check_remote_release_exists() {
    local date_str=$1
    local url="https://github.com/${GITHUB_REPO}/releases/download/${date_str}/qlib_bin.tar.gz"
    
    if wget --spider -q "$url" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 函数：创建备份
create_backup() {
    echo "创建数据备份..."
    mkdir -p "$BACKUP_DIR"
    if [ -d "$QLIB_DATA_DIR" ]; then
        local backup_name="cn_data_backup_$TIMESTAMP"
        cp -r "$QLIB_DATA_DIR" "$BACKUP_DIR/$backup_name"
        echo "备份已创建: $BACKUP_DIR/$backup_name"
    else
        echo "警告: $QLIB_DATA_DIR 不存在，跳过备份"
    fi
}

# 函数：清理旧备份，只保留最新的
cleanup_old_backups() {
    echo "清理旧备份..."
    if [ -d "$BACKUP_DIR" ]; then
        # 获取所有备份，按修改时间排序，保留最新的
        local backup_count=$(ls -1 "$BACKUP_DIR" | wc -l)
        if [ "$backup_count" -gt 1 ]; then
            # 保留最新的备份，删除其他的
            ls -1t "$BACKUP_DIR" | tail -n +2 | xargs -I {} rm -rf "$BACKUP_DIR/{}"
            echo "已清理旧备份，保留最新备份"
        fi
    fi
}

# 函数：验证解压结果
verify_extraction() {
    local expected_date=$1
    
    if [ ! -d "$QLIB_DATA_DIR" ]; then
        echo "错误: 解压失败，$QLIB_DATA_DIR 不存在"
        exit 1
    fi

    # 检查 calendars/day.txt 文件
    local calendar_file="$QLIB_DATA_DIR/calendars/day.txt"
    if [ ! -f "$calendar_file" ]; then
        echo "错误: 缺少日历文件 $calendar_file"
        exit 1
    fi

    # 读取文件最后一行（最后一个日期）
    local last_date=$(tail -n 1 "$calendar_file" | tr -d '\r\n' | xargs)
    
    if [ -z "$last_date" ]; then
        echo "错误: 无法读取日历文件的最后一行"
        exit 1
    fi

    echo "日历文件最后日期: $last_date"
    
    # 如果提供了期望日期，进行验证
    if [ -n "$expected_date" ] && [ "$expected_date" != "未知" ]; then
        if [ "$last_date" != "$expected_date" ]; then
            echo "警告: 日历文件最后日期 ($last_date) 与期望日期 ($expected_date) 不匹配"
            echo "继续执行，但请注意数据可能不是最新版本"
        else
            echo "✓ 日期验证通过: 日历文件最后日期与期望日期一致"
        fi
    else
        echo "日历文件最后日期: $last_date"
    fi

    echo "数据验证成功"
}

# 函数：从文件名中提取日期（如果可能）
# 支持格式：YYYY-MM-DD 或 YYYYMMDD
extract_date_from_filename() {
    local filename=$1
    local date_str=""
    
    # 首先尝试提取 YYYY-MM-DD 格式
    if [[ "$filename" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
        date_str="${BASH_REMATCH[1]}"
    # 然后尝试提取 YYYYMMDD 格式（8位数字）
    elif [[ "$filename" =~ ([0-9]{4})([0-9]{2})([0-9]{2}) ]]; then
        # 将YYYYMMDD转换为YYYY-MM-DD格式
        local year="${BASH_REMATCH[1]}"
        local month="${BASH_REMATCH[2]}"
        local day="${BASH_REMATCH[3]}"
        date_str="${year}-${month}-${day}"
    fi
    
    echo "$date_str"
}

# 函数：解析命令行参数
parse_arguments() {
    LOCAL_TAR_FILE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                LOCAL_TAR_FILE="$2"
                shift 2
                ;;
            -h|--help)
                echo "使用方法:"
                echo "  自动下载: $0"
                echo "  使用本地tar包: $0 --file /path/to/qlib_bin_YYYYMMDD.tar.gz"
                echo "  使用本地tar包（简短）: $0 -f /path/to/qlib_bin_YYYYMMDD.tar.gz"
                echo ""
                echo "参数说明:"
                echo "  -f, --file    指定本地tar包文件路径（必须以 .tar.gz 结尾）"
                echo "  -h, --help    显示帮助信息"
                echo ""
                echo "文件名格式要求:"
                echo "  - 文件名必须以 .tar.gz 结尾"
                echo "  - 建议在文件名中包含日期，格式为 YYYYMMDD（例如: qlib_bin_20251211.tar.gz）"
                echo "  - 也支持 YYYY-MM-DD 格式（例如: qlib_bin_2025-12-11.tar.gz）"
                echo "  - 脚本会自动将文件复制到 data 目录并按照规则命名"
                exit 0
                ;;
            *)
                echo "未知参数: $1"
                echo "使用 $0 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
}

# 主逻辑
main() {
    # 先检查是否是帮助请求
    for arg in "$@"; do
        if [[ "$arg" == "-h" ]] || [[ "$arg" == "--help" ]]; then
            parse_arguments "$@"
            return
        fi
    done
    
    echo "开始更新投资数据..."
    
    # 解析命令行参数
    parse_arguments "$@"
    
    TAR_FILE=""
    FOUND_DATE=""
    
    # 如果用户指定了本地tar包文件
    if [ -n "$LOCAL_TAR_FILE" ]; then
        # 检查文件是否存在
        if [ ! -f "$LOCAL_TAR_FILE" ]; then
            echo "错误: 指定的文件不存在: $LOCAL_TAR_FILE"
            exit 1
        fi
        
        # 检查文件是否可读
        if [ ! -r "$LOCAL_TAR_FILE" ]; then
            echo "错误: 文件不可读: $LOCAL_TAR_FILE"
            exit 1
        fi
        
        # 检查文件扩展名必须是 .tar.gz
        if [[ ! "$LOCAL_TAR_FILE" =~ \.tar\.gz$ ]]; then
            echo "错误: 文件名必须以 .tar.gz 结尾"
            echo "当前文件名: $LOCAL_TAR_FILE"
            exit 1
        fi
        
        # 显示文件信息
        echo "文件大小: $(ls -lh "$LOCAL_TAR_FILE" | awk '{print $5}')"
        
        # 尝试从文件名中提取日期
        FOUND_DATE=$(extract_date_from_filename "$LOCAL_TAR_FILE")
        if [ -z "$FOUND_DATE" ]; then
            echo "警告: 无法从文件名中提取日期，使用当前日期"
            FOUND_DATE=$(get_workday_date)
        fi
        echo "检测到的数据日期: $FOUND_DATE"
        
        # 创建data目录
        mkdir -p "$DATA_DIR"
        
        # 检查data目录中是否已有相同日期的文件
        DATA_TAR_FILE="$DATA_DIR/qlib_bin_${FOUND_DATE}.tar.gz"
        if [ -f "$DATA_TAR_FILE" ]; then
            echo "提示: data目录中已存在相同日期的文件: $DATA_TAR_FILE"
            echo "文件大小: $(ls -lh "$DATA_TAR_FILE" | awk '{print $5}')"
            echo "为避免重复更新，退出脚本"
            exit 0
        else
            # 将文件复制到data目录，按照规则命名：qlib_bin_YYYY-MM-DD.tar.gz
            echo "复制文件到data目录: $DATA_TAR_FILE"
            cp "$LOCAL_TAR_FILE" "$DATA_TAR_FILE"
            
            if [ $? -ne 0 ]; then
                echo "错误: 复制文件失败"
                exit 1
            fi
            
            echo "使用本地tar包: $LOCAL_TAR_FILE"
            echo "data目录中的副本: $DATA_TAR_FILE"
            TAR_FILE="$DATA_TAR_FILE"
        fi
    else
        # 自动下载模式
        # 1. 计算初始下载日期（工作日）
        DOWNLOAD_DATE=$(get_workday_date)
        echo "初始下载日期: $DOWNLOAD_DATE"

        # 2. 创建data目录
        mkdir -p "$DATA_DIR"

        # 3. 查找可用的tar包（先检查本地，再检查远程）
        # 首先检查本地是否已有当天的tar包
        if LOCAL_FILE=$(check_local_tar_exists "$DOWNLOAD_DATE"); then
            echo "发现本地已有该日期的tar包: $LOCAL_FILE"
            TAR_FILE="$LOCAL_FILE"
            FOUND_DATE="$DOWNLOAD_DATE"
        # 如果本地没有，检查远程是否存在
        elif check_remote_release_exists "$DOWNLOAD_DATE"; then
            # 检查data目录中是否已有相同日期的文件
            TAR_FILE="$DATA_DIR/qlib_bin_${DOWNLOAD_DATE}.tar.gz"
            if [ -f "$TAR_FILE" ]; then
                echo "提示: data目录中已存在相同日期的文件: $TAR_FILE"
                echo "文件大小: $(ls -lh "$TAR_FILE" | awk '{print $5}')"
                echo "为避免重复更新，退出脚本"
                exit 0
            else
                echo "远程release存在，开始下载: $DOWNLOAD_DATE"
                DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${DOWNLOAD_DATE}/qlib_bin.tar.gz"
                
                if ! wget -O "$TAR_FILE" "$DOWNLOAD_URL"; then
                    echo "错误: 下载失败，请检查网络连接"
                    exit 1
                fi
                FOUND_DATE="$DOWNLOAD_DATE"
            fi
        else
            # 远程不存在，尝试前一个交易日
            echo "远程release不存在，尝试前一个交易日..."
            PREVIOUS_DATE=$(get_previous_trading_day "$DOWNLOAD_DATE")
            echo "尝试日期: $PREVIOUS_DATE"
            
            # 检查本地是否有前一个交易日的tar包
            if LOCAL_FILE=$(check_local_tar_exists "$PREVIOUS_DATE"); then
                echo "发现本地已有前一个交易日的tar包: $LOCAL_FILE"
                TAR_FILE="$LOCAL_FILE"
                FOUND_DATE="$PREVIOUS_DATE"
            # 检查远程是否有前一个交易日的release
            elif check_remote_release_exists "$PREVIOUS_DATE"; then
                # 检查data目录中是否已有相同日期的文件
                TAR_FILE="$DATA_DIR/qlib_bin_${PREVIOUS_DATE}.tar.gz"
                if [ -f "$TAR_FILE" ]; then
                    echo "提示: data目录中已存在相同日期的文件: $TAR_FILE"
                    echo "文件大小: $(ls -lh "$TAR_FILE" | awk '{print $5}')"
                    echo "为避免重复更新，退出脚本"
                    exit 0
                else
                    echo "远程release存在，开始下载: $PREVIOUS_DATE"
                    DOWNLOAD_URL="https://github.com/${GITHUB_REPO}/releases/download/${PREVIOUS_DATE}/qlib_bin.tar.gz"
                    
                    if ! wget -O "$TAR_FILE" "$DOWNLOAD_URL"; then
                        echo "错误: 下载失败，请检查网络连接"
                        exit 1
                    fi
                    FOUND_DATE="$PREVIOUS_DATE"
                fi
            else
                echo "错误: 无法找到可用的release"
                echo "已尝试日期: $DOWNLOAD_DATE, $PREVIOUS_DATE"
                echo "请手动检查: https://github.com/${GITHUB_REPO}/releases"
                echo "或者使用本地文件: $0 --file /path/to/qlib_bin.tar.gz"
                exit 1
            fi
        fi

        echo "使用tar包: $TAR_FILE (日期: $FOUND_DATE)"
    fi

    # 4. 创建备份
    create_backup

    # 5. 删除原有的cn_data数据（备份已完成，可以安全删除）
    if [ -d "$QLIB_DATA_DIR" ]; then
        echo "删除原有的cn_data数据..."
        rm -rf "$QLIB_DATA_DIR"
        if [ $? -ne 0 ]; then
            echo "错误: 删除原有数据失败"
            exit 1
        fi
        echo "原有数据已删除"
    fi

    # 6. 创建新的目录并解压数据
    echo "解压数据到 $QLIB_DATA_DIR"
    mkdir -p "$QLIB_DATA_DIR"
    if ! tar -zxvf "$TAR_FILE" -C "$QLIB_DATA_DIR" --strip-components=1; then
        echo "错误: 解压失败"
        exit 1
    fi

    # 7. 验证解压结果
    verify_extraction "$FOUND_DATE"

    # 8. 保留tar文件（所有文件都保存在data目录中，格式为 qlib_bin_YYYY-MM-DD.tar.gz）
    echo "tar文件已保存在data目录: $TAR_FILE"

    # 9. 清理旧备份
    cleanup_old_backups

    echo "更新完成！"
    echo "使用的数据日期: $FOUND_DATE"
    echo "新数据已安装到: $QLIB_DATA_DIR"
    if [ -d "$BACKUP_DIR" ]; then
        echo "备份保存在: $BACKUP_DIR"
        ls -la "$BACKUP_DIR"
    fi
}

# 执行主函数
main "$@"