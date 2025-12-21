"""
技术指标计算模块

提供MACD和BOLL等技术指标的计算功能。
"""
from typing import Literal
import pandas as pd
import talib

# 周期类型定义
PeriodType = Literal["D", "W", "M", "Q", "Y"]
PERIOD_NAMES = {
    "D": "日线",
    "W": "周线",
    "M": "月线",
    "Q": "季线",
    "Y": "年线",
}

# BOLL参数（日线默认值）
BOLL_DEV = 2.0  # 布林带标准差倍数

# 不同周期的参数配置
PERIOD_PARAMS = {
    "D": {
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "boll_period": 20,
    },
    "W": {
        "macd_fast": 12,  # 周线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_slow": 26,  # 周线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_signal": 9,  # 周线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "boll_period": 20,  # 周线：使用标准BOLL参数(20,2.0)，与同花顺保持一致
    },
    "M": {
        "macd_fast": 12,  # 月线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_slow": 26,  # 月线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_signal": 9,  # 月线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "boll_period": 20,  # 月线：使用标准BOLL参数(20,2.0)，与同花顺保持一致
    },
    "Q": {
        "macd_fast": 12,  # 季线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_slow": 26,  # 季线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_signal": 9,  # 季线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "boll_period": 20,  # 季线：使用标准BOLL参数(20,2.0)，与同花顺保持一致
    },
    "Y": {
        "macd_fast": 12,  # 年线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_slow": 26,  # 年线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "macd_signal": 9,  # 年线：使用标准MACD参数(12,26,9)，与同花顺保持一致
        "boll_period": 20,  # 年线：使用标准BOLL参数(20,2.0)，与同花顺保持一致
    },
}


def calculate_macd(df: pd.DataFrame, period: PeriodType = "D") -> pd.DataFrame:
    """
    计算MACD指标（根据周期动态调整参数）

    Args:
        df: 包含close列的DataFrame
        period: 周期类型，用于选择参数

    Returns:
        DataFrame: 添加了MACD相关列的DataFrame
    """
    df = df.copy()

    # 根据周期获取参数
    params = PERIOD_PARAMS.get(period, PERIOD_PARAMS["D"])
    fast_period = params["macd_fast"]
    slow_period = params["macd_slow"]
    signal_period = params["macd_signal"]

    # 检查数据点数量是否足够计算指标
    min_periods = max(slow_period, signal_period)
    if len(df) < min_periods:
        print(
            f"警告: 数据点数量({len(df)})不足以计算MACD指标(需要至少{min_periods}个数据点，当前周期: {PERIOD_NAMES.get(period, period)})"
        )
        # 如果数据点不足，尝试使用更小的参数
        if len(df) >= 3:
            # 至少需要3个数据点才能计算
            fast_period = min(fast_period, len(df) - 1)
            slow_period = min(slow_period, len(df))
            signal_period = min(signal_period, len(df) - 1)
            print(
                f"  调整参数: fast={fast_period}, slow={slow_period}, signal={signal_period}"
            )
        else:
            # 数据点太少，无法计算
            df["EMA12"] = pd.NA
            df["EMA26"] = pd.NA
            df["DIF"] = pd.NA
            df["DEA"] = pd.NA
            df["MACD"] = pd.NA
            return df

    # 确保参数不超过数据长度，且至少为2（talib要求）
    fast_period = max(2, min(fast_period, len(df)))
    slow_period = max(2, min(slow_period, len(df)))
    signal_period = max(2, min(signal_period, len(df)))

    # 确保slow_period > fast_period
    if slow_period <= fast_period:
        slow_period = min(fast_period + 1, len(df))

    df["EMA12"] = talib.EMA(df["close"], timeperiod=fast_period)
    df["EMA26"] = talib.EMA(df["close"], timeperiod=slow_period)
    df["DIF"] = df["EMA12"] - df["EMA26"]
    df["DEA"] = talib.EMA(df["DIF"], timeperiod=signal_period)
    df["MACD"] = 2 * (df["DIF"] - df["DEA"])
    return df


def calculate_boll(df: pd.DataFrame, period: PeriodType = "D") -> pd.DataFrame:
    """
    计算BOLL指标（布林带）（根据周期动态调整参数）

    Args:
        df: 包含close列的DataFrame
        period: 周期类型，用于选择参数

    Returns:
        DataFrame: 添加了BOLL相关列的DataFrame
    """
    df = df.copy()

    # 根据周期获取参数
    params = PERIOD_PARAMS.get(period, PERIOD_PARAMS["D"])
    boll_period = params["boll_period"]

    # 检查数据点数量是否足够计算指标
    if len(df) < boll_period:
        print(
            f"警告: 数据点数量({len(df)})不足以计算BOLL指标(需要至少{boll_period}个数据点，当前周期: {PERIOD_NAMES.get(period, period)})"
        )
        # 如果数据点不足，尝试使用更小的参数
        if len(df) >= 3:
            boll_period = min(boll_period, len(df))
            print(f"  调整参数: boll_period={boll_period}")
        else:
            # 数据点太少，无法计算
            df["BOLL_UPPER"] = pd.NA
            df["BOLL_MIDDLE"] = pd.NA
            df["BOLL_LOWER"] = pd.NA
            return df

    # 确保参数不超过数据长度，且至少为2（talib要求）
    boll_period = max(2, min(boll_period, len(df)))

    df["BOLL_UPPER"], df["BOLL_MIDDLE"], df["BOLL_LOWER"] = talib.BBANDS(
        df["close"],
        timeperiod=boll_period,
        nbdevup=BOLL_DEV,
        nbdevdn=BOLL_DEV,
        matype=0,
    )
    return df


def calculate_indicators(df: pd.DataFrame, period: PeriodType = "D") -> pd.DataFrame:
    """
    计算所有技术指标（根据周期动态调整参数）

    Args:
        df: 包含OHLCV数据的DataFrame
        period: 周期类型，用于选择参数

    Returns:
        DataFrame: 添加了所有指标列的DataFrame
    """
    df = calculate_macd(df, period)
    df = calculate_boll(df, period)
    return df
