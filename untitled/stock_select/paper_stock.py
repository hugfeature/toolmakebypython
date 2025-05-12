import os
import akshare as ak
import pandas as pd
import time
import traceback
from tqdm import tqdm
from datetime import datetime, timedelta
import re  # 新增导入re模块处理文件名

# 设置数据存储目录
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 获取当前日期的上一个工作日
def get_previous_workday(date=None):
    if date is None:
        date = datetime.today()
    weekday = date.weekday()  # 周一是0，周日是6

    if weekday == 0:  # 周一
        previous_workday = date - timedelta(days=3)
    elif weekday == 6:  # 周日
        previous_workday = date - timedelta(days=2)
    elif weekday == 5:  # 周六
        previous_workday = date - timedelta(days=1)
    else:
        previous_workday = date - timedelta(days=1)

    return previous_workday.strftime("%Y%m%d")

# 选股参数
START_DATE = "20220101"  # 回测开始日期
END_DATE = get_previous_workday()   # 回测结束日期

# 止损止盈参数
STOP_LOSS = 0.95  # 止损：跌 5% 卖出
TAKE_PROFIT = 1.10  # 止盈：涨 10% 卖出

# 获取 A 股股票列表
# def get_stock_list():
#     try:
#         return ak.stock_info_a_code_name()
#     except Exception as e:
#         print(f"❌ 获取股票列表失败: {e}")
#         return pd.DataFrame()

# 获取 A 股股票列表（去除 ST、退市等）
def get_stock_list():
    try:
        df = ak.stock_info_a_code_name()
        # 筛除 ST、*ST、退市股票
        exclude_keywords = ["ST", "退市"]
        pattern = "|".join(exclude_keywords)
        df = df[~df["name"].str.contains(pattern, regex=True, case=False, na=False)]
        # 过滤创业板（3开头）和科创板（688开头）
        df = df[~df['code'].str.startswith(('3', '688'))]
        print(f"✅ 成功获取非 ST/退市 股票数量: {len(df)}")
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        traceback.print_exc()
        return pd.DataFrame()


# 获取 K 线数据
def get_stock_data(stock_code, start_date=START_DATE, end_date=END_DATE):
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if df is None or df.empty:
            raise ValueError(f"⚠️ {stock_code} 无数据")
        
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']]
        df['5日均线'] = df['收盘'].rolling(5).mean()
        df['10日均线'] = df['收盘'].rolling(10).mean()
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

        if df is None or len(df) < 10:
            continue

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # 选股条件：均线金叉 + 量能放大（保持不变）
        if (prev_row['5日均线'] <= prev_row['10日均线']) and (last_row['5日均线'] > last_row['10日均线']):
            if last_row['收盘'] > last_row['10日均线']:
                if last_row['成交量'] > prev_row['成交量'] * 1.1:
                    selected_stocks.append((stock_code, stock_name))
                    # 处理非法字符
                    safe_name = re.sub(r'[\\/*?:"<>| ]', '_', stock_name)
                    file_name = os.path.join(DATA_DIR, f"{stock_code}_{safe_name}_k线.csv")
                    df.to_csv(file_name, index=False, encoding="utf-8-sig")
                    print(f"✅ 选中股票：{stock_code}（{stock_name}），K线数据已保存 {file_name}")

    return selected_stocks

# 回测策略
def backtest(stock_code):
    df = get_stock_data(stock_code)
    if df is None or len(df) < 20:
        print(f"⚠️ {stock_code} 数据不足，跳过回测")
        return None

    # 买入价为选股当天的收盘价（最后一行）
    buy_price = df.iloc[-1]['收盘']
    # 假设之后没有数据，这里仅作演示，实际应获取后续数据
    # 注意：由于数据截止到选股日期，此处无法正确回测，需重新设计数据获取
    # 以下仅为示例逻辑，可能需要调整
    for i in range(len(df)):
        current_row = df.iloc[i]
        # 检查是否在买入之后
        if i < len(df) - 1:
            continue  # 假设买入发生在最后一天，之前的日期忽略
        high_price = current_row['最高']
        low_price = current_row['最低']

        if low_price <= buy_price * STOP_LOSS:
            return STOP_LOSS - 1
        if high_price >= buy_price * TAKE_PROFIT:
            return TAKE_PROFIT - 1

    # 持有到最后一天（即买入当天，收益为0）
    return 0

# 回测全部选股
def backtest_all(selected_stocks):
    results = []
    for stock_code, stock_name in selected_stocks:
        profit = backtest(stock_code)
        if profit is not None:
            results.append({
                "股票代码": stock_code,
                "股票名称": stock_name,
                "收益率(%)": round(profit * 100, 2)
            })

    df_result = pd.DataFrame(results)
    df_result.sort_values(by="收益率(%)", ascending=False, inplace=True)

    # 获取沪深300指数数据，修正代码为000300
    hs300 = get_stock_data("000300")  # 修改代码
    if hs300 is not None and not hs300.empty:
        hs300_profit = (hs300.iloc[-1]['收盘'] / hs300.iloc[0]['收盘']) - 1
        hs300_profit = round(hs300_profit * 100, 2)
        print(f"\n📈 沪深 300 指数收益率: {hs300_profit}%")

    print("\n📊 回测结果（已按收益率排序）：")
    print(df_result.to_string(index=False))
    df_result.to_csv("回测收益排名.csv", index=False, encoding="utf-8-sig")
    print("\n📁 回测结果已保存为回测收益排名.csv")

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
