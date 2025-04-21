import os
import akshare as ak
import pandas as pd
import time
import traceback
from tqdm import tqdm
from datetime import datetime, timedelta

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
        # # 筛除 ST、*ST、退市股票
        exclude_keywords = ["ST","退市"]
        pattern = "|".join(exclude_keywords)
        print(f'过滤前：{df}' )
        df = df[~df["name"].str.contains(pattern,regex=True,case=False, na=False)]
        print(f'过滤后：{df}' )
        # df = df[~df['name'].str.contains(patter, regex=True,case=False, na=False)]
            # df = df[df['name'].str.contains(kw)]

        # # 只保留 6 位数字代码的主板类股票
        # # df = df[df['code'].str.match(r'^\d{6}$')]

        # print(f"✅ 成功获取非 ST/退市 股票数量: {len(df)}")
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        traceback.print_exc()
        return pd.DataFrame()
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

if __name__ == "__main__":
    END_DATE = get_previous_workday()
    print(END_DATE)
    print (type(END_DATE))