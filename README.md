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

### 计划功能

- **股票基本信息获取**
  - 通过Tushare API获取个股基本信息
  - 通过akshare获取股票列表和基本信息
  - 数据清洗和标准化处理

- **财务信息获取**
  - 财务报表数据（资产负债表、利润表、现金流量表）
  - 财务指标计算
  - 历史财务数据归档

- **行业信息获取**
  - 行业分类信息
  - 行业指数数据
  - 行业关联关系

## 项目结构

```
stock_data/
├── data/                          # 数据存储目录
│   └── qlib_bin_YYYY-MM-DD.tar.gz # qlib行情数据压缩包
├── update_from_github_release.sh  # qlib数据更新脚本
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
bash update_from_github_release.sh
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
bash update_from_github_release.sh --file /path/to/qlib_bin_YYYYMMDD.tar.gz

# 使用简短参数
bash update_from_github_release.sh -f /path/to/qlib_bin_YYYYMMDD.tar.gz
```

#### 查看帮助信息

```bash
bash update_from_github_release.sh --help
```

### 3. 数据存储位置

- **Qlib数据**: `~/.qlib/qlib_data/cn_data/`
- **数据备份**: `~/.qlib/backup/`
- **下载的tar包**: `./data/qlib_bin_YYYY-MM-DD.tar.gz`

## 数据源说明

### Qlib行情数据

- **来源**: GitHub Release ([chenditc/investment_data](https://github.com/chenditc/investment_data))
- **数据内容**: 中国A股历史行情数据（OHLCV）
- **更新频率**: 每日更新
- **数据格式**: qlib标准格式

### Tushare（计划中）

- **用途**: 获取个股基本信息、财务数据
- **API**: 需要注册获取Token
- **数据内容**: 
  - 股票基本信息
  - 财务报表数据
  - 财务指标

### AKShare（计划中）

- **用途**: 获取股票列表、行业信息
- **数据内容**:
  - 股票列表和基本信息
  - 行业分类信息
  - 行业指数数据

## 使用示例

### 更新Qlib数据

```bash
# 自动下载最新数据
bash update_from_github_release.sh

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
bash update_from_github_release.sh -f ./data/qlib_bin_2025-12-11.tar.gz
```

## 注意事项

1. **数据备份**: 脚本会自动备份现有数据，但建议在重要操作前手动备份
2. **网络连接**: 自动下载模式需要稳定的网络连接
3. **磁盘空间**: 确保有足够的磁盘空间存储数据（建议至少10GB）
4. **权限问题**: 确保对 `~/.qlib/` 目录有读写权限

## 开发计划

- [ ] 集成Tushare API获取财务数据
- [ ] 集成AKShare获取行业信息
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

