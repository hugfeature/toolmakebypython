import os
import akshare as ak
import pandas as pd
import time
from tqdm import tqdm  # 用于显示进度条

# 创建存储数据的文件夹
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 获取A股股票列表
def get_stock_list():
    try:
        stock_list = ak.stock_info_a_code_name()
        return stock_list
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return pd.DataFrame()

# 获取个股K线数据
def get_stock_data(stock_code, start_date="20240101", end_date="20240401"):
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if df is None or df.empty:
            raise ValueError(f"⚠️ {stock_code} 无数据")
        
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']]
        df['5日均线'] = df['收盘'].rolling(5).mean()
        df['10日均线'] = df['收盘'].rolling(10).mean()
        df['成交量5日均'] = df['成交量'].rolling(5).mean()
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

    for index, row in tqdm(stock_list.iterrows(), total=len(stock_list)):  # 显示进度条
        stock_code = row['code']  # 股票代码
        stock_name = row['name']  # 股票名称

        df = get_stock_data(stock_code)

        if df is None or len(df) < 10:
            continue  # 数据不足，跳过

        last_row = df.iloc[-1]  # 取最后一天数据
        prev_row = df.iloc[-2]  # 取前一天数据

        # 选股策略
        if (prev_row['5日均线'] <= prev_row['10日均线']) and (last_row['5日均线'] > last_row['10日均线']):
            if last_row['收盘'] > last_row['10日均线']:  
                if last_row['成交量'] > last_row['成交量5日均'] * 1.1:  
                    selected_stocks.append((stock_code, stock_name))
                    
                    # 保存 K 线数据
                    file_name = os.path.join(DATA_DIR, f"{stock_code}_{stock_name}_k线.csv")
                    df.to_csv(file_name, index=False, encoding="utf-8-sig")
                    print(f"✅ 选中股票：{stock_code}（{stock_name}），K线数据已保存 {file_name}")

    return selected_stocks

# 运行选股
if __name__ == "__main__":
    start_time = time.time()
    stocks = stock_selection()
    
    if stocks:
        print("\n🎯 今日推荐股票：", stocks)
    else:
        print("\n⚠️ 今天没有符合条件的股票")
    
    end_time = time.time()
    print(f"⏳ 运行时间: {round(end_time - start_time, 2)} 秒")
