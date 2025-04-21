# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import talib
import datetime
import time
import os
import traceback
import matplotlib.pyplot as plt

# === 调用 AKShare API 获取非 ST 股 ===
def get_stock_list():
    try:
        df = ak.stock_info_a_code_name()
        exclude_keywords = ['ST', '*ST', '退']
        for keyword in exclude_keywords:
            df = df[~df['name'].str.contains(keyword, case=False, na=False)]
        print(f"✅ 成功获取非 ST 股 {len(df)} 支")
        return list(zip(df['code'], df['name']))
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []

# === 获取单支股的 K 线历史 ===
def get_stock_data(code):
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20220101", end_date=datetime.datetime.today().strftime("%Y%m%d"), adjust="qfq")
        df = df.rename(columns={"日期": "date", "收盘": "close", "开盘": "open", "最高": "high", "最低": "low", "成交量": "volume"})
        df['date'] = pd.to_datetime(df['date'])
        df.set_index("date", inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        return df
    except Exception as e:
        print(f"❌ [{code}] 数据失败: {e}")
        traceback.print_exc()
        return None

# === 回测策略 ===
def backtest(code, name):
    df = get_stock_data(code)
    if df is None or len(df) < 60:
        return None

    try:
        # === 计算指标 ===
        df['ma20'] = talib.SMA(df['close'], timeperiod=20)
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['macd_diff'], _, _ = talib.MACD(df['close'])

        df.dropna(inplace=True)

        capital = 30000
        position = 0
        entry_price = 0
        stop_loss = 0.95  # 止损 5%
        take_profit = 1.10  # 止盈 10%
        portfolio_values = []

        for i in range(1, len(df)):
            price_now = df['close'].iloc[i]
            if position == 0:
                if df['close'].iloc[i] > df['ma20'].iloc[i] and df['rsi'].iloc[i] < 70 and df['macd_diff'].iloc[i] > 0:
                    position = capital / price_now
                    entry_price = price_now
            elif position > 0:
                if price_now < entry_price * stop_loss or price_now > entry_price * take_profit:
                    capital = position * price_now
                    position = 0
            portfolio = capital if position == 0 else position * price_now
            portfolio_values.append(portfolio)

        if position > 0:
            capital = position * df['close'].iloc[-1]
            portfolio_values.append(capital)

        profit_pct = (capital - 30000) / 30000

        # 绘制收益图
        plt.figure(figsize=(10, 4))
        plt.plot(portfolio_values, label=f"{code} {name} 收益轨迹")
        plt.title(f"{code} {name} 收益曲线")
        plt.xlabel("交易日")
        plt.ylabel("资产净值")
        plt.legend()
        os.makedirs("profit_charts", exist_ok=True)
        plt.savefig(f"profit_charts/{code}_{name}.png")
        plt.close()

        return profit_pct

    except Exception as e:
        print(f"❌ [{code}] 回测异常: {e}")
        traceback.print_exc()
        return None

# === 批量选股 + 回测并排序 ===
def run():
    stock_list = get_stock_list()
    results = []
    os.makedirs("kline_csv", exist_ok=True)

    for code, name in stock_list:
        df = get_stock_data(code)
        if df is not None:
            df.to_csv(f"kline_csv/{code}_{name}.csv")
            profit = backtest(code, name)
            if profit is not None:
                results.append({"code": code, "name": name, "profit": round(profit * 100, 2)})

    df_result = pd.DataFrame(results)
    df_result.sort_values(by="profit", ascending=False, inplace=True)
    df_result.reset_index(drop=True, inplace=True)
    df_result.to_csv("backtest_result.csv", index=False, encoding="utf-8-sig")
    print("\n📅 回测结果已保存 backtest_result.csv")
    print(df_result)  # 打印所有结果

if __name__ == "__main__":
    run()