# Stock Data - 中国A股行情数据准备工具

本项目用于准备中国A股的行情数据，为本地量化交易提供数据支持。项目包含从GitHub下载qlib行情数据并更新到本地，同时也会通过Tushare、akshare等数据源获取股票的其它基本信息，包括个股基本信息、财务信息、行业信息等。

## 功能特性

### 已实现功能

- **Qlib行情数据更新**
  - 自动从GitHub Release下载最新的qlib行情数据
  - 支持手动指定本地tar包文件进行更新
  - 自动备份现有数据，确保数据安全
  - 智能日期检测，自动选择最新的交易日数据
  - 数据验证机制，确保数据完整性

- **A股股票列表获取和存储**
  - 使用AKShare API获取A股股票列表
  - 自动识别股票市场（上海/深圳）
  - 支持获取股票上市日期
  - 批量存储到Dolt数据库
  - 支持数据更新和去重

- **股票扩展数据获取和存储**
  - ✅ 公司信息：企业性质（央企国资控股、民企、外资等）、实际控制人、主营产品
  - ✅ 行业信息：行业名称、行业代码、概念板块、地区
  - ✅ 股东信息：前十大股东、持股比例、持股变化
  - ✅ 市值信息：总市值、流通市值、总股本、流通股本
  - ✅ 财务数据：资产负债表、利润表、现金流量表
  - ✅ 财务指标：ROE、ROA、毛利率、净利率等

- **日线行情数据获取和存储**
  - ✅ 使用AKShare获取日线行情数据（腾讯、东方财富数据源）
  - ✅ 使用Tushare获取日线行情数据（专业数据源，需要积分）
  - ✅ 自动检测最新日期，只获取新数据
  - ✅ 内置API频率限制保护，避免超出调用限制

### 计划功能

- **数据增强**
  - 通过Tushare API获取更详细的财务数据
  - 历史财务数据批量归档
  - 财务指标自动计算
  - 行业指数数据获取

- **数据分析和可视化**
  - 数据质量检查工具
  - 数据可视化工具
  - 数据报表生成

- **自动化**
  - 定时任务自动更新数据
  - 数据变更通知
  - 数据备份自动化

## 项目结构

```
stock_data/
├── src/                           # Python源代码目录
│   └── __init__.py                # Python包初始化文件
├── qlib/                          # Qlib相关工具目录
│   ├── data/                      # 数据存储目录
│   │   └── qlib_bin_YYYY-MM-DD.tar.gz # qlib行情数据压缩包
│   └── update_from_github_release.sh  # qlib数据更新脚本
├── database/                      # 数据库相关配置和脚本
│   ├── docker-compose.yml         # Docker Compose配置
│   ├── config.yaml                # Dolt数据库配置
│   ├── a_stock_schema.md          # 股票数据库表结构文档
│   └── ...                        # 其他数据库相关文件
├── .gitignore                     # Git忽略文件配置
└── README.md                      # 项目说明文档
```

## 环境要求

- **操作系统**: macOS / Linux
- **Python**: Python 3.x（用于日期计算）
- **工具**: 
  - `wget`（用于下载数据）
  - `tar`（用于解压数据）
  - `bash`（脚本执行环境）

## 安装和使用

### 1. 克隆项目

```bash
git clone <repository-url>
cd stock_data
```

### 2. 使用Qlib数据更新脚本

#### 自动下载最新数据

```bash
bash qlib/update_from_github_release.sh
```

脚本会自动：
- 检测当前工作日
- 从GitHub Release下载最新的qlib数据
- 备份现有数据到 `~/.qlib/backup/`
- 解压并安装数据到 `~/.qlib/qlib_data/cn_data/`
- 验证数据完整性

#### 使用本地tar包

```bash
# 使用完整路径
bash qlib/update_from_github_release.sh --file /path/to/qlib_bin_YYYYMMDD.tar.gz

# 使用简短参数
bash qlib/update_from_github_release.sh -f /path/to/qlib_bin_YYYYMMDD.tar.gz
```

#### 查看帮助信息

```bash
bash qlib/update_from_github_release.sh --help
```

### 3. 初始化数据库（首次使用前）

```bash
# 创建数据库（如果不存在）
mysql -h 127.0.0.1 -P 13306 -u root -p -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 执行初始化脚本（包含所有表结构）
mysql -h 127.0.0.1 -P 13306 -u root -p a_stock < database/migrations/001_init_database.sql
```

或使用Docker：

```bash
# 创建数据库（如果不存在）
docker exec stock_data_dolt mysql -uroot -ptest -e "CREATE DATABASE IF NOT EXISTS a_stock;"

# 执行初始化脚本
docker exec -i stock_data_dolt mysql -uroot -ptest a_stock < database/migrations/001_init_database.sql
```

**注意**: 如果数据库已存在且需要重新创建，请先删除数据库：
```bash
mysql -h 127.0.0.1 -P 13306 -u root -p -e "DROP DATABASE IF EXISTS a_stock;"
# 然后重新执行上面的初始化步骤
```

### 4. 获取A股股票列表并存入数据库

#### 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 启动数据库服务

```bash
cd database
docker-compose up -d
```

#### 运行股票列表获取脚本

基本用法（快速，不获取上市日期）：
```bash
python src/fetch_stocks.py
```

获取上市日期（较慢，但信息更完整）：
```bash
python src/fetch_stocks.py --with-list-date
```

查看帮助：
```bash
python src/fetch_stocks.py --help
```

### 5. 更新股票扩展数据

更新单只股票的所有扩展数据：
```bash
python src/update_stock_data.py --code 000001
```

更新所有股票的行业信息：
```bash
python src/update_stock_data.py --data-type industry
```

更新所有股票的股东信息：
```bash
python src/update_stock_data.py --data-type shareholders
```

更新所有股票的市值信息：
```bash
python src/update_stock_data.py --data-type market_value
```

更新所有股票的财务数据：
```bash
python src/update_stock_data.py --data-type financial
```

更新所有股票的公司信息（企业性质、实际控制人、主营产品）：
```bash
python src/update_stock_data.py --data-type company_info
```

更新所有股票的所有扩展数据（推荐使用延迟避免API限制）：
```bash
python src/update_stock_data.py --delay 1.0
```

### 6. 使用Tushare更新日线行情数据

#### 配置Tushare Token

在 `database/.env` 文件中添加：
```bash
TUSHARE_TOKEN=your_tushare_token_here
```

#### 更新单只股票

```bash
# 从最新日期开始更新（自动检测）
python src/update_tushare_daily.py --code 000001

# 指定日期范围
python src/update_tushare_daily.py --code 000001 --start-date 20230101 --end-date 20231201
```

#### 批量更新所有股票

```bash
# 从最新日期开始更新
python src/update_tushare_daily.py --all

# 指定日期范围
python src/update_tushare_daily.py --all --start-date 20230101 --end-date 20231201

# 自定义批次大小和延迟（推荐）
python src/update_tushare_daily.py --all --batch-size 20 --delay 1.0
```

#### 注意事项

- **API限制**: Tushare有调用频率限制，程序已内置自动延迟机制
- **默认延迟**: 客户端默认延迟0.2秒，批量更新建议使用 `--delay 1.0` 或更长
- **数据格式**: 自动转换成交量（手→股）和成交额（千元→元）
- **智能更新**: 自动检测数据库中的最新日期，只获取新数据

### 7. 数据存储位置

- **Qlib数据**: `~/.qlib/qlib_data/cn_data/`
- **数据备份**: `~/.qlib/backup/`
- **下载的tar包**: `qlib/data/qlib_bin_YYYY-MM-DD.tar.gz`
- **Dolt数据库**: `database/dolt-data/`

## 数据源说明

### Qlib行情数据

- **来源**: GitHub Release ([chenditc/investment_data](https://github.com/chenditc/investment_data))
- **数据内容**: 中国A股历史行情数据（OHLCV）
- **更新频率**: 每日更新
- **数据格式**: qlib标准格式

### Tushare（已实现）

- **用途**: 获取日线行情数据、个股基本信息、财务数据
- **API**: 需要注册获取Token，配置在 `database/.env` 文件中
- **数据内容**: 
  - ✅ 日线行情数据（OHLCV）
  - 股票基本信息（计划中）
  - 财务报表数据（计划中）
  - 财务指标（计划中）
- **API限制**:
  - 免费版：每日500次，每分钟30次
  - Pro版：每日2000次，每分钟可能更多
- **自动延迟机制**: 客户端内置延迟机制（默认0.2秒），确保不会超出API限制

### AKShare（已实现）

- **用途**: 获取股票列表、行业信息
- **数据内容**:
  - ✅ 股票列表和基本信息（已实现）
  - 行业分类信息（计划中）
  - 行业指数数据（计划中）

## 使用示例

### 更新Qlib数据

```bash
# 自动下载最新数据
bash qlib/update_from_github_release.sh

# 输出示例：
# 开始更新投资数据...
# 初始下载日期: 2025-12-11
# 远程release存在，开始下载: 2025-12-11
# 创建数据备份...
# 备份已创建: ~/.qlib/backup/cn_data_backup_20251211_143022
# 解压数据到 ~/.qlib/qlib_data/cn_data
# ✓ 日期验证通过: 日历文件最后日期与期望日期一致
# 更新完成！
```

### 使用本地数据包

```bash
# 如果已经下载了数据包
bash qlib/update_from_github_release.sh -f qlib/data/qlib_bin_2025-12-11.tar.gz
```

## 注意事项

1. **数据备份**: 脚本会自动备份现有数据，但建议在重要操作前手动备份
2. **网络连接**: 自动下载模式需要稳定的网络连接
3. **磁盘空间**: 确保有足够的磁盘空间存储数据（建议至少10GB）
4. **权限问题**: 确保对 `~/.qlib/` 目录有读写权限

## Python模块说明

详细的Python模块使用说明请参考 [src/README.md](src/README.md)

### 模块结构

- `src/config.py` - 数据库配置模块
- `src/db.py` - 数据库连接和操作模块
- `src/akshare_client.py` - AKShare数据获取客户端
- `src/stock_service.py` - 股票数据服务模块
- `src/fetch_stocks.py` - 主程序：获取股票列表并存入数据库

## 开发计划

- [x] 集成AKShare获取股票列表（已完成）
- [x] 集成AKShare获取行业信息（已完成）
- [x] 集成AKShare获取股东数据（已完成）
- [x] 集成AKShare获取市值数据（已完成）
- [x] 集成AKShare获取财务数据（已完成）
- [x] 集成Tushare API获取日线行情数据（已完成）
- [ ] 集成Tushare API获取更详细的财务数据
- [ ] 数据清洗和标准化处理
- [ ] 数据更新自动化脚本
- [ ] 数据质量检查工具
- [ ] 数据可视化工具

## 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

[待定]

## 联系方式

如有问题或建议，请通过Issue反馈。

