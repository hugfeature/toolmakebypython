import yfinance as yf
import pandas as pd

# 获取苹果公司股票数据
stock = 'AAPL'
df = yf.download(stock, start="2023-01-01", end="2024-01-01")

# 显示前5行数据
if df is not None:
    print(df.head(10))
