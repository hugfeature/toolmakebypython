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
    
# RSI 超卖反弹（近6日 RSI < 30 → 当前 RSI 上穿 30）
def calculate_rsi(series, period=6):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# 获取 K 线数据
def get_stock_data(stock_code, start_date=START_DATE, end_date=END_DATE):
    try:
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if df is None or df.empty:
            raise ValueError(f"⚠️ {stock_code} 无数据")
        
        df = df[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']]
        df['5日均线'] = df['收盘'].rolling(5).mean()
        df['10日均线'] = df['收盘'].rolling(10).mean()
        df['RSI6'] = calculate_rsi(df['收盘'], 6)
        return df
    except Exception as e:
        print(f"❌ 获取 {stock_code} 数据失败: {e}")
        return None

# # 选股逻辑
# def stock_selection():
#     stock_list = get_stock_list()
#     selected_stocks = []
    
#     if stock_list.empty:
#         print("❌ 无法获取股票列表，程序退出")
#         return []

#     print(f"📊 正在分析 {len(stock_list)} 只股票...")

#     for index, row in tqdm(stock_list.iterrows(), total=len(stock_list)):
#         stock_code = row['code']
#         stock_name = row['name']

#         df = get_stock_data(stock_code)

#         if df is None or len(df) < 10:
#             continue

#         last_row = df.iloc[-1]
#         prev_row = df.iloc[-2]

#         # 选股条件：均线金叉 + 量能放大（保持不变）
#         if (prev_row['5日均线'] <= prev_row['10日均线']) and (last_row['5日均线'] > last_row['10日均线']):
#             if last_row['收盘'] > last_row['10日均线']:
#                 if last_row['成交量'] > prev_row['成交量'] * 1.1:
#                     # 新增：突破近 20 日前高
#                     recent_high = df['最高'].iloc[-21:-1].max()
#                     if last_row['收盘'] <= recent_high:
#                         continue  # 没有突破，跳过
#                     selected_stocks.append((stock_code, stock_name))
#                     # 处理非法字符
#                     safe_name = re.sub(r'[\\/*?:"<>| ]', '_', stock_name)
#                     file_name = os.path.join(DATA_DIR, f"{stock_code}_{safe_name}_k线.csv")
#                     df.to_csv(file_name, index=False, encoding="utf-8-sig")
#                     print(f"✅ 选中股票：{stock_code}（{stock_name}），K线数据已保存 {file_name}")
        

#     return selected_stocks
def stock_selection():
    stock_list = get_stock_list()
    selected_stocks = []
    selection_logs = []

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

        # 添加技术指标
        df['5日均线'] = df['收盘'].rolling(5).mean()
        df['10日均线'] = df['收盘'].rolling(10).mean()
        df['20日最高'] = df['最高'].rolling(window=20).max()

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # ============ 选股逻辑 ============ #
        # 条件1：均线金叉（5日均线上穿10日均线）
        gold_cross = (prev_row['5日均线'] <= prev_row['10日均线']) and (last_row['5日均线'] > last_row['10日均线'])

        # 条件2：放量（当日成交量 > 前一日 10%）
        volume_up = last_row['成交量'] > prev_row['成交量'] * 1.1

        # 条件3：收盘价突破20日新高
        breakout = last_row['收盘'] > prev_row['20日最高']

        if gold_cross and volume_up and breakout:
            selected_stocks.append((stock_code, stock_name))

            # 保存K线文件
            safe_name = re.sub(r'[\\/*?:"<>| ]', '_', stock_name)
            file_path = os.path.join(DATA_DIR, f"{stock_code}_{safe_name}_k线.csv")
            df.to_csv(file_path, index=False, encoding="utf-8-sig")

            print(f"✅ 选中股票：{stock_code}（{stock_name}），K线已保存 {file_path}")

            # 记录选股日志
            selection_logs.append({
                "股票代码": stock_code,
                "股票名称": stock_name,
                "选股日期": last_row['日期'],
                "收盘价": last_row['收盘'],
                "5日均线": round(last_row['5日均线'], 2),
                "10日均线": round(last_row['10日均线'], 2),
                "成交量": last_row['成交量'],
                "前日20日最高": round(prev_row['20日最高'], 2),
                "收盘是否创新高": breakout,
                "放量": volume_up,
                "均线金叉": gold_cross
            })

    # 生成日志 CSV
    if selection_logs:
        df_log = pd.DataFrame(selection_logs)
        log_filename = f"选股日志_{datetime.now().strftime('%Y%m%d')}.csv"
        df_log.to_csv(log_filename, index=False, encoding="utf-8-sig")
        print(f"\n📁 选股日志已保存：{log_filename}")

    return selected_stocks

# 获取选股日后 n 天的 K 线数据用于真实回测
def get_future_data(stock_code, from_date, days=10):
    start = datetime.strptime(from_date, "%Y%m%d") + timedelta(days=1)
    end = start + timedelta(days=days)
    return get_stock_data(stock_code, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))

# # 回测策略
# def backtest(stock_code):
#     df = get_stock_data(stock_code)
#     if df is None or len(df) < 20:
#         print(f"⚠️ {stock_code} 数据不足，跳过回测")
#         return None

#     # 买入价为选股当天的收盘价（最后一行）
#     buy_price = df.iloc[-1]['收盘']
#     # 假设之后没有数据，这里仅作演示，实际应获取后续数据
#     # 注意：由于数据截止到选股日期，此处无法正确回测，需重新设计数据获取
#     # 以下仅为示例逻辑，可能需要调整
#     for i in range(len(df)):
#         current_row = df.iloc[i]
#         # 检查是否在买入之后
#         if i < len(df) - 1:
#             continue  # 假设买入发生在最后一天，之前的日期忽略
#         high_price = current_row['最高']
#         low_price = current_row['最低']

#         if low_price <= buy_price * STOP_LOSS:
#             return STOP_LOSS - 1
#         if high_price >= buy_price * TAKE_PROFIT:
#             return TAKE_PROFIT - 1

#     # 持有到最后一天（即买入当天，收益为0）
#     return 0
def backtest(stock_code, buy_date, buy_price):
    df_future = get_future_data(stock_code, buy_date, days=10)
    if df_future is None or df_future.empty:
        print(f"⚠️ {stock_code} 无法获取未来数据，跳过回测")
        return None

    for _, row in df_future.iterrows():
        high_price = row['最高']
        low_price = row['最低']
        if low_price <= buy_price * STOP_LOSS:
            return round((STOP_LOSS - 1) * 100, 2)
        if high_price >= buy_price * TAKE_PROFIT:
            return round((TAKE_PROFIT - 1) * 100, 2)

    # 持有至最后一天
    final_price = df_future.iloc[-1]['收盘']
    return round((final_price / buy_price - 1) * 100, 2)

def backtest_all(selected_stocks, hold_days=5):
    results = []

    for stock_code, stock_name in selected_stocks:
        try:
            # 获取完整历史数据（包含选股日之后）
            df_all = get_stock_data(stock_code)
            if df_all is None or len(df_all) < 30:
                print(f"⚠️ {stock_code} 数据不足，跳过")
                continue

            # 获取选股日（最后一行）
            select_day = df_all.iloc[-1]['日期']
            buy_price = df_all.iloc[-1]['收盘']

            # 获取选股日之后 n 天数据
            df_future = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=(datetime.strptime(select_day, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d"),
                end_date=(datetime.strptime(select_day, "%Y-%m-%d") + timedelta(days=hold_days + 10)).strftime("%Y%m%d"),
                adjust="qfq"
            )

            if df_future is None or df_future.empty:
                print(f"⚠️ {stock_code} 无未来数据，跳过")
                continue

            # 取前 hold_days 天
            df_future = df_future.head(hold_days)

            # 默认持有收益
            final_price = df_future.iloc[-1]['收盘']
            max_price = df_future['最高'].max()
            min_price = df_future['最低'].min()

            profit = 0  # 收益率
            exit_reason = "持有到期"

            if min_price <= buy_price * STOP_LOSS:
                profit = STOP_LOSS - 1
                exit_reason = "止损"
            elif max_price >= buy_price * TAKE_PROFIT:
                profit = TAKE_PROFIT - 1
                exit_reason = "止盈"
            else:
                profit = (final_price / buy_price) - 1

            results.append({
                "股票代码": stock_code,
                "股票名称": stock_name,
                "选股日期": select_day,
                "买入价": round(buy_price, 2),
                "卖出价": round(final_price, 2),
                "最大涨幅": round((max_price / buy_price - 1) * 100, 2),
                "最大回撤": round((min_price / buy_price - 1) * 100, 2),
                "收益率(%)": round(profit * 100, 2),
                "退出原因": exit_reason
            })
        except Exception as e:
            print(f"❌ 回测 {stock_code} 出错: {e}")
            traceback.print_exc()
            continue

    df_result = pd.DataFrame(results)
    df_result.sort_values(by="收益率(%)", ascending=False, inplace=True)

    # 输出结果
    print("\n📊 回测结果（按收益率排序）：")
    print(df_result.to_string(index=False))

    filename = f"回测收益排名_{datetime.now().strftime('%Y%m%d')}.csv"
    df_result.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"\n📁 回测结果已保存为 {filename}")

# # 回测全部选股
# def backtest_all(selected_stocks):
#     results = []
#     for stock_code, stock_name in selected_stocks:
#         profit = backtest(stock_code,buy_date, buy_price)
#         if profit is not None:
#             results.append({
#                 "股票代码": stock_code,
#                 "股票名称": stock_name,
#                 "收益率(%)": round(profit * 100, 2)
#             })

#     df_result = pd.DataFrame(results)
#     df_result.sort_values(by="收益率(%)", ascending=False, inplace=True)

#     # 获取沪深300指数数据，修正代码为000300
#     hs300 = get_stock_data("000300")  # 修改代码
#     if hs300 is not None and not hs300.empty:
#         hs300_profit = (hs300.iloc[-1]['收盘'] / hs300.iloc[0]['收盘']) - 1
#         hs300_profit = round(hs300_profit * 100, 2)
#         print(f"\n📈 沪深 300 指数收益率: {hs300_profit}%")

#     print("\n📊 回测结果（已按收益率排序）：")
#     print(df_result.to_string(index=False))
#     df_result.to_csv("回测收益排名.csv", index=False, encoding="utf-8-sig")
#     print("\n📁 回测结果已保存为回测收益排名.csv")

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
