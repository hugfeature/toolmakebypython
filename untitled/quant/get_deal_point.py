import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

stock = 'AAPL'
df = yf.download(stock, start="2023-01-01", end="2024-01-01")

# 显示前5行数据
if df is not None:
    print(df.head(10))
    # 计算均线
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

    # 生成买卖信号
    df['Signal'] = 0
    df.loc[df['SMA10'] > df['SMA50'], 'Signal'] = 1  # 买入
    df.loc[df['SMA10'] < df['SMA50'], 'Signal'] = -1  # 卖出

    # 画图
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Stock Price', color='black')
    plt.plot(df.index, df['SMA10'], label='10-Day SMA', color='blue')
    plt.plot(df.index, df['SMA50'], label='50-Day SMA', color='red')

    # 画买入卖出点
    plt.scatter(df.index[df['Signal'] == 1], df['Close'][df['Signal'] == 1], marker='^', color='g', label='Buy Signal', alpha=1)
    plt.scatter(df.index[df['Signal'] == -1], df['Close'][df['Signal'] == -1], marker='v', color='r', label='Sell Signal', alpha=1)

    plt.legend()
    plt.title('Moving Average Crossover Strategy')
    plt.show()

