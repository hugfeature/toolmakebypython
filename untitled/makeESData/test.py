import sys
import threading
import warnings

import requests
import datetime


# 设置索引名字
base_index_name = "test"  # 索引名称前缀
for i in range(100):
    # 起始日期
    start = "20230625"
    for j in range(180):
        # 设置时间从今天开始向前180天
        start_date = datetime.datetime.strptime(start, '%Y%m%d')
        index_date = start_date - datetime.timedelta(j)
        time1 = index_date.strftime('%Y-%m-%d %H:%M:%S')
        time2 = index_date.timestamp() * 1000
        index_name = f"{base_index_name}-{i}-{index_date.strftime('%Y%m%d')}"
        print(index_name)