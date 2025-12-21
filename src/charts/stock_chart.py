"""
股票K线图绘制工具
支持MACD和BOLL指标的可视化

"""

import os
import sys
from datetime import datetime
from typing import Literal, Optional, Tuple

# 支持的图片格式
ImageFormat = Literal["png", "svg"]

# 添加项目路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from ..services.fetch_data_service import fetch_data_service
from .indicators import (
    PeriodType,
    PERIOD_NAMES,
    calculate_indicators,
)

# ==================== 常量配置 ====================
DEFAULT_CHART_DIR = "generated_charts"  # 默认图表保存目录
DEFAULT_DPI = 150  # 默认图片分辨率
DEFAULT_FIGSIZE = (20, 12)  # 默认图表尺寸（增加高度以便MACD更清晰）
DEFAULT_PERIOD = "D"  # 默认周期（日线）
DEFAULT_FORMAT: ImageFormat = "png"  # 默认图片格式


class StockChartGenerator:
    """股票K线图生成器类"""
    
    def __init__(
        self,
        chart_dir: str = None,
        dpi: int = DEFAULT_DPI,
        figsize: Tuple[int, int] = DEFAULT_FIGSIZE,
        image_format: ImageFormat = DEFAULT_FORMAT,
    ):
        """
        初始化股票图表生成器
        
        Args:
            chart_dir: 图表保存目录，如果为None则使用默认目录
            dpi: 图片分辨率（仅对PNG格式有效，SVG为矢量格式不需要DPI）
            figsize: 图表尺寸
            image_format: 图片格式，可选 'png' 或 'svg'（默认: 'png'）
        """
        self.chart_dir = chart_dir or os.path.join(
            os.path.dirname(__file__), "..", "..", DEFAULT_CHART_DIR
        )
        self.dpi = dpi
        self.figsize = figsize
        self.image_format = image_format
        
        # 配置中文字体
        self.chinese_font_prop = self._setup_chinese_font()
        plt.rcParams["axes.unicode_minus"] = False
        
        # 创建自定义样式
        self.custom_style = self._create_custom_style()
    
    def _setup_chinese_font(self) -> Optional[fm.FontProperties]:
        """
        配置中文字体支持

        Returns:
            FontProperties: 中文字体属性对象，如果找不到则返回None
        """
        chinese_font_path = None

        # 查找可用的中文字体文件
        for font in fm.fontManager.ttflist:
            if "Arial Unicode" in font.name:
                chinese_font_path = font.fname
                break
            elif "STHeiti" in font.name:
                chinese_font_path = font.fname
                break

        # 设置字体
        if chinese_font_path:
            chinese_font_prop = fm.FontProperties(fname=chinese_font_path)
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.sans-serif"] = [
                chinese_font_prop.get_name(),
                "Arial Unicode MS",
                "STHeiti",
            ]
            return chinese_font_prop
        else:
            # 备用方案：使用字体名称
            plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "STHeiti", "Heiti TC"]
            return None

    def _create_custom_style(self) -> str:
        """
        创建支持中文的自定义mplfinance样式

        Returns:
            str: 样式名称或样式对象
        """
        try:
            custom_style = mpf.make_mpf_style(
                base_mpf_style="charles",
                marketcolors=mpf.make_marketcolors(
                    up="red",
                    down="green",
                    edge="inherit",
                    wick="inherit",
                    volume="inherit",
                ),
                gridstyle=":",
                y_on_right=False,
                facecolor="white",
                edgecolor="black",
                figcolor="white",
                gridcolor="lightgray",
                rc={
                    "font.family": "sans-serif",
                    "font.sans-serif": plt.rcParams["font.sans-serif"],
                    "axes.unicode_minus": False,
                },
            )
            return custom_style
        except Exception as e:
            print(f"创建自定义样式失败，使用默认样式: {e}")
            return "charles"
    
    def resample_data(self, df: pd.DataFrame, period: PeriodType) -> pd.DataFrame:
        """
        将日线数据转换为指定周期（周线、月线、季线、年线）

        Args:
            df: 日线数据，索引必须是DatetimeIndex
            period: 目标周期，可选值：'D'（日线）、'W'（周线）、'M'（月线）、'Q'（季线）、'Y'（年线）

        Returns:
            DataFrame: 转换后的数据框
        """
        if df is None or df.empty:
            return df

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("数据索引必须是 DatetimeIndex 类型")

        # 如果是日线，直接返回
        if period == "D":
            return df.copy()

        # 定义重采样规则（使用新的pandas规则以避免FutureWarning）
        resample_rules = {
            "W": "W",  # 周线：每周最后一个交易日
            "M": "ME",  # 月线：每月最后一个交易日
            "Q": "QE",  # 季线：每季度最后一个交易日
            "Y": "YE",  # 年线：每年最后一个交易日
        }

        if period not in resample_rules:
            raise ValueError(
                f"不支持的周期类型: {period}，支持的类型: {list(resample_rules.keys())}"
            )

        rule = resample_rules[period]

        # 重采样：使用OHLC规则
        # open: 第一个值
        # high: 最大值
        # low: 最小值
        # close: 最后一个值
        # volume: 总和
        resampled = pd.DataFrame()
        resampled["open"] = df["open"].resample(rule).first()
        resampled["high"] = df["high"].resample(rule).max()
        resampled["low"] = df["low"].resample(rule).min()
        resampled["close"] = df["close"].resample(rule).last()
        resampled["volume"] = df["volume"].resample(rule).sum()

        # 如果有其他列，也保留（如openinterest）
        other_cols = [col for col in df.columns if col not in resampled.columns]
        for col in other_cols:
            if col in df.columns:
                resampled[col] = df[col].resample(rule).last()

        # 删除包含NaN的行
        resampled = resampled.dropna()

        return resampled
    
    def _get_date_format_string(self, date_range_days: int) -> str:
        """
        根据数据跨度选择合适的日期格式字符串

        Args:
            date_range_days: 日期跨度（天数）

        Returns:
            str: 日期格式字符串
        """
        if date_range_days > 365 * 2:
            return "%Y-%m"
        elif date_range_days > 180:
            return "%Y-%m"
        elif date_range_days > 30:
            return "%Y-%m-%d"
        else:
            return "%Y-%m-%d"

    def _format_xaxis_dates(self, axes_list: list, plot_data: pd.DataFrame, bottom_ax) -> None:
        """
        格式化X轴日期显示

        Args:
            axes_list: 所有axes的列表
            plot_data: 绘图数据（包含日期索引）
            bottom_ax: 底部axes（用于设置日期标签）
        """
        if not isinstance(plot_data.index, pd.DatetimeIndex):
            return

        try:
            x_ticks = bottom_ax.get_xticks()
            x_lim = bottom_ax.get_xlim()

            # mplfinance使用数字索引，需要转换为日期
            if x_lim[1] < len(plot_data) * 2:
                # X轴是数字索引，需要转换为日期
                valid_ticks = [tick for tick in x_ticks if 0 <= tick < len(plot_data)]

                if len(valid_ticks) > 0:
                    # 使用现有的刻度位置
                    tick_indices = [int(tick) for tick in valid_ticks]
                    tick_dates = [plot_data.index[idx] for idx in tick_indices]
                else:
                    # 创建新的刻度位置
                    num_ticks = min(12, max(5, len(plot_data) // 100))
                    tick_indices = [
                        int(i * (len(plot_data) - 1) / (num_ticks - 1))
                        for i in range(num_ticks)
                    ]
                    tick_dates = [plot_data.index[idx] for idx in tick_indices]

                # 根据数据跨度选择合适的日期格式
                date_range = (plot_data.index[-1] - plot_data.index[0]).days
                date_format_str = self._get_date_format_string(date_range)
                date_labels = [date.strftime(date_format_str) for date in tick_dates]

                # 对所有axes设置相同的日期刻度
                for ax in axes_list:
                    ax.set_xticks(tick_indices)

                # 只对底部axes设置标签
                bottom_ax.set_xticklabels(date_labels, rotation=45, ha="right")
            else:
                # X轴已经是日期格式，设置日期格式化器
                for ax in axes_list:
                    ax.xaxis_date()

                date_range = (plot_data.index[-1] - plot_data.index[0]).days
                date_format = mdates.DateFormatter(self._get_date_format_string(date_range))

                # 对所有axes设置格式化器
                for ax in axes_list:
                    ax.xaxis.set_major_formatter(date_format)
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
        except Exception as e:
            print(f"设置日期格式化失败: {e}，使用默认格式")

    def _create_add_plots(self, df: pd.DataFrame) -> list:
        """
        创建需要添加到图表的额外绘图对象

        Args:
            df: 包含指标数据的DataFrame

        Returns:
            list: addplot对象列表
        """
        add_plots = []

        # BOLL指标添加到主图（panel=0）
        # 检查BOLL指标是否存在且有效
        if all(col in df.columns for col in ["BOLL_UPPER", "BOLL_MIDDLE", "BOLL_LOWER"]):
            boll_valid = (
                df["BOLL_UPPER"].notna().any()
                and df["BOLL_MIDDLE"].notna().any()
                and df["BOLL_LOWER"].notna().any()
            )
            if boll_valid:
                add_plots.extend(
                    [
                        mpf.make_addplot(
                            df["BOLL_UPPER"],
                            color="red",  # 上轨：红色
                            width=1.5,
                            label="BOLL Upper",
                            panel=0,
                            alpha=0.8,
                        ),
                        mpf.make_addplot(
                            df["BOLL_MIDDLE"],
                            color="blue",  # 中轨：蓝色（与上下轨区分）
                            width=1.5,
                            label="BOLL Middle",
                            panel=0,
                            alpha=0.8,
                        ),
                        mpf.make_addplot(
                            df["BOLL_LOWER"],
                            color="green",  # 下轨：绿色（与上轨区分）
                            width=1.5,
                            label="BOLL Lower",
                            panel=0,
                            alpha=0.8,
                        ),
                    ]
                )

        # MACD指标添加到独立面板（panel=2，与成交量panel=1分离）
        # 检查MACD指标是否存在且有效
        if all(col in df.columns for col in ["DIF", "DEA", "MACD"]):
            macd_valid = (
                df["DIF"].notna().any()
                and df["DEA"].notna().any()
                and df["MACD"].notna().any()
            )
            if macd_valid:
                # MACD柱需要根据正负值设置不同颜色
                # 创建正负值分别的Series
                macd_positive = df["MACD"].copy()
                macd_positive[macd_positive < 0] = 0  # 负值设为0
                macd_negative = df["MACD"].copy()
                macd_negative[macd_negative > 0] = 0  # 正值设为0

                add_plots.extend(
                    [
                        mpf.make_addplot(
                            df["DIF"], color="blue", width=1.5, label="DIF", panel=2
                        ),
                        mpf.make_addplot(
                            df["DEA"], color="orange", width=1.5, label="DEA", panel=2
                        ),
                        # MACD正值柱：红色（MACD > 0）
                        mpf.make_addplot(
                            macd_positive,
                            type="bar",
                            color="red",
                            width=0.8,
                            label="MACD+",
                            panel=2,
                            alpha=0.7,
                        ),
                        # MACD负值柱：绿色（MACD < 0）
                        mpf.make_addplot(
                            macd_negative,
                            type="bar",
                            color="green",
                            width=0.8,
                            label="MACD-",
                            panel=2,
                            alpha=0.7,
                        ),
                    ]
                )

        return add_plots

    def _apply_chinese_fonts(
        self, fig, axes_list: list
    ) -> None:
        """
        为图表应用中文字体

        Args:
            fig: matplotlib figure对象
            axes_list: axes列表
        """
        if not self.chinese_font_prop:
            return

        for ax in axes_list:
            # 设置所有文本对象
            for text in ax.texts:
                text.set_fontproperties(self.chinese_font_prop)

            # 设置axes标题
            title = ax.get_title()
            if title:
                ax.title.set_fontproperties(self.chinese_font_prop)

            # 设置坐标轴标签
            xlabel = ax.get_xlabel()
            ylabel = ax.get_ylabel()
            if xlabel:
                ax.xaxis.label.set_fontproperties(self.chinese_font_prop)
            if ylabel:
                ax.yaxis.label.set_fontproperties(self.chinese_font_prop)

            # 设置刻度标签字体
            for label in ax.get_xticklabels():
                if label.get_text():
                    label.set_fontproperties(self.chinese_font_prop)
            for label in ax.get_yticklabels():
                if label.get_text():
                    label.set_fontproperties(self.chinese_font_prop)

    def _plot_stock_chart(
        self,
        plot_data: pd.DataFrame,
        add_plots: list,
        title: str,
        filepath: str,
    ) -> None:
        """
        绘制股票K线图并保存

        Args:
            plot_data: 绘图数据（OHLCV）
            add_plots: 额外绘图对象列表（可以为空）
            title: 图表标题
            filepath: 保存路径
        """
        # 准备绘图参数
        plot_kwargs = {
            "type": "candle",
            "style": self.custom_style,
            "ylabel": "价格",
            "volume": True,
            "figsize": self.figsize,
            "show_nontrading": False,
            "returnfig": True,
            "warn_too_much_data": 10000,
        }

        # 如果有额外绘图对象，添加addplot和panel_ratios
        if add_plots:
            plot_kwargs["addplot"] = add_plots
            # 检查是否有MACD指标（panel=2）
            has_macd = any(hasattr(ap, "panel") and ap.panel == 2 for ap in add_plots)
            if has_macd:
                # 如果有MACD，使用(3, 1, 2)让MACD面板有更多空间
                # mplfinance要求panel_ratios长度等于面板数量
                # panel=0: K线图, panel=1: 成交量, panel=2: MACD
                plot_kwargs["panel_ratios"] = (3, 1, 2)  # K线图, 成交量, MACD
            else:
                # 如果没有MACD，只有K线图和成交量
                plot_kwargs["panel_ratios"] = (3, 1)  # K线图, 成交量

        # 使用mplfinance绘制图表
        fig, axes = mpf.plot(plot_data, **plot_kwargs)

        if fig is None:
            # 如果returnfig失败，使用原来的方法
            fallback_kwargs = {
                "type": "candle",
                "style": self.custom_style,
                "title": title,
                "ylabel": "价格",
                "volume": True,
                "figsize": self.figsize,
                "show_nontrading": False,
                "savefig": dict(fname=filepath, dpi=self.dpi, bbox_inches="tight"),
                "warn_too_much_data": 10000,
            }
            if add_plots:
                fallback_kwargs["addplot"] = add_plots
                # 检查是否有MACD指标（panel=2）
                has_macd = any(hasattr(ap, "panel") and ap.panel == 2 for ap in add_plots)
                if has_macd:
                    fallback_kwargs["panel_ratios"] = (3, 1, 2)
                else:
                    fallback_kwargs["panel_ratios"] = (3, 1)
            mpf.plot(plot_data, **fallback_kwargs)
            return

        # 设置中文标题
        if self.chinese_font_prop:
            fig.suptitle(title, fontproperties=self.chinese_font_prop, fontsize=16, y=0.995)

        # 获取所有axes
        axes_list = fig.get_axes()

        # 为MACD面板添加标题和分隔线，使其更清晰独立
        if len(axes_list) >= 3 and self.chinese_font_prop:
            # axes_list顺序通常是：K线图、成交量、MACD
            # 为MACD面板（最后一个axes）添加标题
            macd_ax = axes_list[-1]
            macd_ax.set_ylabel(
                "MACD指标", fontproperties=self.chinese_font_prop, fontsize=12, fontweight="bold"
            )

            # 在MACD面板上方添加分隔线，使其与成交量面板更明显分开
            # 获取MACD面板的位置
            pos = macd_ax.get_position()
            # 在MACD面板上方绘制一条分隔线
            fig.add_artist(
                plt.Line2D(
                    [pos.x0, pos.x1],
                    [pos.y1, pos.y1],
                    transform=fig.transFigure,
                    color="gray",
                    linewidth=2,
                    linestyle="--",
                    alpha=0.5,
                )
            )

            # 添加图例说明（如果MACD数据存在）
            if add_plots:
                # 检查是否有MACD相关的addplot
                has_macd = any(
                    "DIF" in str(ap) or "DEA" in str(ap) or "MACD" in str(ap)
                    for ap in add_plots
                )
                if has_macd:
                    # 在MACD面板右上角添加图例说明
                    macd_ax.text(
                        0.98,
                        0.95,
                        "DIF(蓝) | DEA(橙) | MACD柱(红/绿)",
                        transform=macd_ax.transAxes,
                        fontproperties=self.chinese_font_prop,
                        fontsize=9,
                        verticalalignment="top",
                        horizontalalignment="right",
                        bbox=dict(
                            boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.3
                        ),
                    )

        # 格式化X轴日期
        if axes_list:
            self._format_xaxis_dates(axes_list, plot_data, axes_list[-1])

        # 应用中文字体
        self._apply_chinese_fonts(fig, axes_list)

        # 保存图片
        # SVG是矢量格式，不需要DPI参数
        save_kwargs = {"bbox_inches": "tight"}
        if self.image_format == "svg":
            save_kwargs["format"] = "svg"
        else:
            save_kwargs["dpi"] = self.dpi
        
        fig.savefig(filepath, **save_kwargs)
        plt.close(fig)

    def generate_filename(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: PeriodType = "D",
        data_source: str = "supabase",
        image_format: Optional[ImageFormat] = None,
    ) -> str:
        """
        生成图表文件名和路径

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            period: 周期类型
            data_source: 数据源，默认 'supabase'
            image_format: 图片格式，如果为None则使用实例的默认格式

        Returns:
            str: 完整的文件路径
        """
        os.makedirs(self.chart_dir, exist_ok=True)
        start_date_str = start_date.replace("-", "")
        end_date_str = end_date.replace("-", "")
        period_name = PERIOD_NAMES.get(period, period)
        format_ext = (image_format or self.image_format).lower()
        filename = f"{stock_code}_{start_date_str}_{end_date_str}_{period_name}_{data_source}_MACD_BOLL.{format_ext}"
        return os.path.join(self.chart_dir, filename)

    def generate(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: PeriodType = DEFAULT_PERIOD,
        image_format: Optional[ImageFormat] = None,
    ) -> str:
        """
        生成股票K线图

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)，如果为None则使用该股票的最早交易日期
            end_date: 结束日期 (YYYY-MM-DD)，如果为None则使用该股票的最新交易日期
            period: 周期类型，可选值：'D'（日线）、'W'（周线）、'M'（月线）、'Q'（季线）、'Y'（年线）
            image_format: 图片格式，可选 'png' 或 'svg'，如果为None则使用实例的默认格式

        Returns:
            str: 保存的图表文件路径
        """
        # 检查股票代码
        if not stock_code:
            raise ValueError("股票代码不能为空")

        # 处理日期：如果没有指定日期，使用该股票的最早/最新交易日期
        if start_date is None:
            start_date = fetch_data_service.get_earliest_trade_date(stock_code)
            if start_date:
                print(f"未指定开始日期，使用该股票最早交易日期: {start_date}")
            else:
                raise ValueError(f"数据库中没有{stock_code}的数据")
        
        if end_date is None:
            end_date = fetch_data_service.get_latest_trade_date(stock_code)
            if end_date:
                print(f"未指定结束日期，使用该股票最新交易日期: {end_date}")
            else:
                raise ValueError(f"数据库中没有{stock_code}的数据")

        # 获取股票数据（始终获取日线数据）
        df = fetch_data_service.fetch_stock_data(
            stock_code, start_date, end_date
        )

        # 如果指定了非日线周期，进行重采样
        if period != "D":
            period_name = PERIOD_NAMES.get(period, period)
            print(f"将日线数据转换为{period_name}数据...")
            df = self.resample_data(df, period)
            print(f"重采样后数据点数量: {len(df)}")

        # 计算技术指标（在重采样后计算，确保指标基于正确的周期）
        df = calculate_indicators(df, period)

        # 准备绘图数据
        plot_data = df[["open", "high", "low", "close", "volume"]].copy()
        if not isinstance(plot_data.index, pd.DatetimeIndex):
            plot_data.index = pd.to_datetime(plot_data.index)

        # 打印数据信息
        period_name = PERIOD_NAMES.get(period, period)
        print(f"{period_name}数据日期范围: {plot_data.index[0]} 到 {plot_data.index[-1]}")
        print(f"数据点数量: {len(plot_data)}")
        print(f"数据列: {plot_data.columns.tolist()}")

        # 创建额外绘图对象
        add_plots = self._create_add_plots(df)

        # 获取股票名称
        stock_name = fetch_data_service.get_stock_name_from_supabase(stock_code)
        if stock_name and stock_name != stock_code:
            display_name = f"{stock_name}({stock_code})"
        else:
            display_name = stock_code

        # 生成文件名（如果指定了格式，使用指定的格式，否则使用实例的默认格式）
        output_format = image_format or self.image_format
        filepath = self.generate_filename(
            stock_code,
            start_date,
            end_date,
            period,
            image_format=output_format
        )

        # 生成标题
        title = (
            f"{display_name}从{start_date}至{end_date}的{period_name}行情数据"
        )

        # 临时设置输出格式（如果指定了格式参数）
        original_format = self.image_format
        if image_format:
            self.image_format = image_format
        
        try:
            # 绘制图表
            self._plot_stock_chart(
                plot_data, add_plots, title, filepath
            )
        finally:
            # 恢复原始格式
            self.image_format = original_format

        print(f"图表已保存到: {filepath}")
        return filepath

