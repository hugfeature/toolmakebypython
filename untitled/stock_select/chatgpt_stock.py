import os
import akshare as ak
import pandas as pd
import time
import traceback
from tqdm import tqdm
from datetime import datetime, timedelta
import re  # 新增导入re模块处理文件名
import json

def load_config(config_path="config.json"):
    default_config = {
        "hold_days": 5,
        "take_profit_rate": 1.10,
        "stop_loss_rate": 0.95,
        "log_path": "log/stock_selection_log.csv",
        "kline_save_dir": "data",
        "exclude_keywords": ["ST", "退市"],
        "exclude_code_prefixes": ["3", "688"],
        "benchmark_index": "000300",
        "save_kline": True,
        "generate_log": True
    }

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        print(f"⚙️ 未找到配置文件，已生成默认配置文件：{config_path}")
        return default_config

    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)
        config = {**default_config, **user_config}  # 用用户配置覆盖默认
        print(f"⚙️ 成功读取配置文件：{config_path}")
        return config
    except Exception as e:
        print(f"❌ 读取配置文件失败：{e}")
        return default_config

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

# 根据配置文件读取
def stock_selection(config):
    from datetime import datetime
    selected_stocks = []
    selection_date = datetime.now().strftime("%Y-%m-%d")

    try:
        stock_list = ak.stock_info_a_code_name()

        # 过滤ST、退市
        exclude_keywords = config.get("exclude_keywords", [])
        pattern = "|".join(exclude_keywords)
        stock_list = stock_list[~stock_list["name"].str.contains(pattern, regex=True, case=False, na=False)]

        # 过滤创业板（3开头）和科创板（688开头）
        exclude_prefixes = tuple(config.get("exclude_code_prefixes", []))
        stock_list = stock_list[~stock_list["code"].str.startswith(exclude_prefixes)]

        print(f"✅ 有效股票数量：{len(stock_list)}")
    except Exception as e:
        print(f"❌ 获取股票列表失败：{e}")
        return []

    log_data = []

    for _, row in tqdm(stock_list.iterrows(), total=len(stock_list)):
        code, name = row["code"], row["name"]
        df = get_stock_data(code)

        if df is None or len(df) < 20:
            continue

        df["5日均线"] = df["收盘"].rolling(5).mean()
        df["10日均线"] = df["收盘"].rolling(10).mean()
        recent_high = df["最高"][-20:-1].max()  # 过去19天最高价（不含最后一天）

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # 选股条件
        if (
            prev["5日均线"] <= prev["10日均线"]
            and last["5日均线"] > last["10日均线"]
            and last["收盘"] > last["10日均线"]
            and last["成交量"] > prev["成交量"] * 1.1
            and last["最高"] > recent_high  # 突破近20日最高
        ):
            selected_stocks.append((code, name))
            print(f"🎯 选中股票：{code}（{name}）")

            if config.get("save_kline", True):
                safe_name = re.sub(r'[\\/*?:"<>| ]', '_', name)
                save_path = os.path.join(config["kline_save_dir"], f"{code}_{safe_name}_k线.csv")
                df.to_csv(save_path, index=False, encoding="utf-8-sig")

            if config.get("generate_log", True):
                log_data.append({
                    "日期": selection_date,
                    "股票代码": code,
                    "股票名称": name,
                    "收盘价": last["收盘"],
                    "成交量": last["成交量"],
                    "突破20日高": recent_high,
                    "5日均线": last["5日均线"],
                    "10日均线": last["10日均线"]
                })

    # 写入日志 CSV
    if config.get("generate_log", True) and log_data:
        log_path = config.get("log_path", "log/stock_selection_log.csv")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        df_log = pd.DataFrame(log_data)
        if os.path.exists(log_path):
            df_log.to_csv(log_path, mode="a", header=False, index=False, encoding="utf-8-sig")
        else:
            df_log.to_csv(log_path, index=False, encoding="utf-8-sig")
        print(f"📝 选股日志已写入：{log_path}")

    return selected_stocks

# 加入了持有时间和自动止盈止损率,读取配置文件
def run_strategy(hold_days, take_profit_rate, stop_loss_rate, config):
    start_time = time.time()

    selected_stocks = stock_selection(config)

    if not selected_stocks:
        print("⚠️ 今天没有符合条件的股票")
        return

    print("\n📊 开始回测所选股票...")

    results = []

    for code, name in selected_stocks:
        df = get_stock_data(code)
        if df is None or len(df) < 20:
            continue

        buy_price = df.iloc[-1]["收盘"]
        future_data = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=(datetime.today() + timedelta(days=1)).strftime("%Y%m%d"),
            end_date=(datetime.today() + timedelta(days=hold_days + 5)).strftime("%Y%m%d"),
            adjust="qfq"
        )

        if future_data is None or future_data.empty:
            print(f"⚠️ {code} 无法获取未来 K 线数据，跳过")
            continue

        profit = 0
        for i, row in future_data.iterrows():
            high = row["最高"]
            low = row["最低"]
            close = row["收盘"]

            if low <= buy_price * stop_loss_rate:
                profit = stop_loss_rate - 1
                break
            elif high >= buy_price * take_profit_rate:
                profit = take_profit_rate - 1
                break
        else:
            profit = (close / buy_price) - 1

        results.append({
            "股票代码": code,
            "股票名称": name,
            "收益率(%)": round(profit * 100, 2)
        })

    df_result = pd.DataFrame(results)
    # 删除空值，并强制将收益率列转为浮点数
    df_result = df_result.dropna(subset=["收益率(%)"])
    df_result["收益率(%)"] = pd.to_numeric(df_result["收益率(%)"], errors="coerce")
    df_result = df_result.dropna(subset=["收益率(%)"])
    df_result.sort_values(by="收益率(%)", ascending=False, inplace=True)
    df_result.to_csv("回测收益排名.csv", index=False, encoding="utf-8-sig")

    print("\n📈 回测完成，收益排名如下：")
    print(df_result.to_string(index=False))
    print("📁 回测结果已保存为：回测收益排名.csv")

    end_time = time.time()
    print(f"⏳ 总耗时: {round(end_time - start_time, 2)} 秒")




if __name__ == "__main__":
    config = load_config()

    # 创建必要的目录
    os.makedirs(config["kline_save_dir"], exist_ok=True)
    os.makedirs(os.path.dirname(config["log_path"]), exist_ok=True)

    run_strategy(
        hold_days=config["hold_days"],
        take_profit_rate=config["take_profit_rate"],
        stop_loss_rate=config["stop_loss_rate"],
        config=config
    )

