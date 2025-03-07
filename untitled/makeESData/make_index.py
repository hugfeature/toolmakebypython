import datetime
from elasticsearch import Elasticsearch
import ssl

# 创建ES客户端对象
es = Elasticsearch(
    ['https://elastic:t*mRUPeeYd8LI3CPY68-@10.130.245.22:9200'],
    verify_certs=False
)

# 索引名称使用日期格式
index_name = 'my_index_{}'.format(datetime.datetime.now().strftime('%Y-%m-%d'))

# 创建索引
es.indices.create(index=index_name)

# 添加文档
doc1 = {
    'timestamp': datetime.datetime.now(),
    'message': 'This is the first document'
}
doc2 = {
    'timestamp': datetime.datetime.now(),
    'message': 'This is the second document'
}
es.index(index=index_name, document=doc1)
es.index(index=index_name, document=doc2)
