import os
import akshare as ak
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

# 设置存储路径
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 选股参数
START_DATE = "20230101"  # 回测开始日期
END_DATE = "20240401"    # 回测结束日期

# 止损止盈参数
STOP_LOSS = 0.95  # 止损 5%
TAKE_PROFIT = 1.10  # 止盈 10%

# 获取 A 股股票列表
def get_stock_list():
    try:
        return ak.stock_info_a_code_name()
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return pd.DataFrame()

# 计算技术指标
def calculate_indicators(df):
    df['5日均线'] = df['收盘'].rolling(5).mean()
    df['10日均线'] = df['收盘'].rolling(10).mean()

    # RSI 指标
    delta = df['收盘'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(14).mean()
    avg_loss = pd.Series(loss).rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD 指标
    df['EMA12'] = df['收盘'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['收盘'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # ATR（真实波幅）指标
    df['TR'] = np.maximum(df['最高'] - df['最低'], 
                          np.maximum(abs(df['最高'] - df['收盘'].shift(1)), 
                                     abs(df['最低'] - df['收盘'].shift(1))))
    df['ATR'] = df['TR'].rolling(14).mean()

    return df

# 获取股票数据
def get_stock_data(stock_code):
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=START_DATE, end_date=END_DATE, adjust="qfq")
        if df is None or df.empty:
            raise ValueError(f"⚠️ {stock_code} 无数据")

        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']]
        df = calculate_indicators(df)
        return df
    except Exception as e:
        print(f"❌ 获取 {stock_code} 数据失败: {e}")
        return None

# 选股逻辑
def stock_selection():
    stock_list = get_stock_list()
    selected_stocks = []
    
    if stock_list.empty:
        print("❌ 无法获取股票列表，程序退出")
        return []

    print(f"📊 正在分析 {len(stock_list)} 只股票...")

    for index, row in tqdm(stock_list.iterrows(), total=len(stock_list)):
        stock_code = row['code']
        stock_name = row['name']

        df = get_stock_data(stock_code)

        if df is None or len(df) < 20:
            continue

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # 选股条件：
        # 1. 均线金叉：5日均线突破 10日均线
        # 2. RSI 在 30~70 之间，避免超买或超卖
        # 3. MACD 上穿信号线，形成买点
        # 4. ATR（真实波幅）不超过收盘价的 5%，避免大波动个股
        if (prev_row['5日均线'] <= prev_row['10日均线']) and (last_row['5日均线'] > last_row['10日均线']):
            if 30 < last_row['RSI'] < 70:
                if last_row['MACD'] > last_row['SIGNAL']:
                    if last_row['ATR'] < last_row['收盘'] * 0.05:
                        selected_stocks.append((stock_code, stock_name))
                        
                        # 保存 K 线数据
                        file_name = os.path.join(DATA_DIR, f"{stock_code}_{stock_name}_k线.csv")
                        df.to_csv(file_name, index=False, encoding="utf-8-sig")
                        print(f"✅ 选中股票：{stock_code}（{stock_name}），K线数据已保存 {file_name}")

    return selected_stocks

# 回测策略
def backtest(stock_code):
    df = get_stock_data(stock_code)

    if df is None or len(df) < 20:
        print(f"⚠️ {stock_code} 数据不足，跳过回测")
        return None

    buy_price = df.iloc[0]['收盘']  # 以第一天收盘价买入
    for i in range(1, len(df)):
        high_price = df.iloc[i]['最高']
        low_price = df.iloc[i]['最低']

        # 止盈止损策略
        if low_price <= buy_price * STOP_LOSS:
            return STOP_LOSS - 1  # 亏 5%
        if high_price >= buy_price * TAKE_PROFIT:
            return TAKE_PROFIT - 1  # 赚 10%

    # 没触发止盈止损，持有到最后一天
    final_price = df.iloc[-1]['收盘']
    return (final_price / buy_price) - 1  # 计算最终收益率

# 回测全部选股
def backtest_all(selected_stocks):
    results = []
    for stock_code, stock_name in selected_stocks:
        profit = backtest(stock_code)
        if profit is not None:
            results.append((stock_code, stock_name, round(profit * 100, 2)))  # 转换为百分比

    # 获取沪深 300 作为基准
    hs300 = get_stock_data("sh000300")  # 沪深 300 指数
    if hs300 is not None:
        hs300_profit = (hs300.iloc[-1]['收盘'] / hs300.iloc[0]['收盘']) - 1
        hs300_profit = round(hs300_profit * 100, 2)
        print(f"\n📈 沪深 300 指数收益率: {hs300_profit}%")

    print("\n📊 回测结果（%）：")
    for stock in results:
        print(f"{stock[1]}（{stock[0]}）收益率: {stock[2]}%")

# 运行选股 & 回测
if __name__ == "__main__":
    start_time = time.time()

    selected_stocks = stock_selection()
    
    if selected_stocks:
        print("\n🎯 今日推荐股票：", selected_stocks)
        backtest_all(selected_stocks)
    else:
        print("\n⚠️ 今天没有符合条件的股票")
    
    end_time = time.time()
    print(f"⏳ 运行时间: {round(end_time - start_time, 2)} 秒")
