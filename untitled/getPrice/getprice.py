import datetime
import requests
import pandas as pd
from openpyxl import Workbook


# 获取当前年月
def get_date():
    today = datetime.datetime.today()
    days_count = datetime.timedelta(days=today.day)
    end_time = today - days_count
    # print(end_time.strftime("%Y%m"))
    return end_time.strftime("%Y%m")


# 获取向前获取一年
date = pd.period_range(end=get_date(), periods=13, freq='M')
with pd.ExcelWriter('car_data.xlsx') as writer:
    for YMdate in date:
        yearmotn = YMdate.strftime('%Y%m')
        # 获取接口
        url = "https://www.dongchedi.com/motor/pc/car/rank_data?aid=1839&count=20&month=" + yearmotn \
              + "&rank_data_type=11&outter_detail_type=3"
        # 发送请求返回数据JSON封装
        html_data = requests.get(url).json()
        # 获取目标数据--汽车销量和排名
        list_data = html_data['data']["list"]
        # padas数据处理
        data = pd.DataFrame(list_data)
        # 按照月份写入Excel不同sheet页面
        data.to_excel(writer, sheet_name=yearmotn, index=False,
                      columns=["series_name", "count", "min_price", "max_price"])
