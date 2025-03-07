import warnings

import requests
import json
from datetime import datetime

# 设置ES集群的URL和身份验证信息
es_url = "https://10.130.245.22:9200"
username = "elastic"
password = "t*mRUPeeYd8LI3CPY68-"

# 创建一个会话，并设置认证信息
session = requests.Session()
session.auth = (username, password)
session.verify = False
# 忽略警告
warnings.filterwarnings("ignore")
# 设置索引名字
base_index_name = "test"  # 索引名称前缀
start_date = datetime.now()  # 起始日期
i = 2
# 添加索引
index_name = f"{base_index_name}-{i}-{start_date.strftime('%Y%m%d')}"
index_mapping = {
    "mappings": {
        "properties": {
            "date": {
                "type": "date",
                "format": "yyyy-MM-dd"
            }
        }
    }
}
index_url = f"{es_url}/{index_name}"
# response = session.put(index_url, json=index_mapping)
response = session.put(index_url)
if response.status_code == 200:
    print(f"索引 {index_name} 创建成功！")
else:
    print(f"索引 {index_name} 创建失败！")

# 添加数据
data = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "message": "Hello, ES!"
}
data_url = f"{es_url}/{index_name}/_doc"
response = session.post(data_url, json=data)
if response.status_code == 201:
    print("数据添加成功！")
else:
    print("数据添加失败！")
