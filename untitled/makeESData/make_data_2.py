from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch(
    ['https://10.130.245.22:9200'],
    basic_auth=('elastic', 't*mRUPeeYd8LI3CPY68-'),
    verify_certs=False
    # scheme="https",
    # port=443,
)

# 索引名称和日期字段名称
base_index_name = "your-index-prefix"  # 索引名称前缀
start_date = datetime.now()  # 起始日期
i = 0
# 添加索引
index_name = f"{base_index_name}-{i}-{start_date.strftime('%Y%m%d')}"
date_field = "date"

# 创建索引
es.indices.create(index=index_name, ignore=400)

# 为数据创建文档
doc = {
    "message": "Your data message",
    date_field: datetime.now().strftime("%Y-%m-%d")  # 或者使用其他日期处理方式
}

# 将文档添加到索引
res = es.index(index=index_name, document=doc)

if res["result"] == "created":
    print("数据添加成功！")
else:
    print("数据添加失败！")

