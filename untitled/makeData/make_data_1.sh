#!/bin/bash

# 定义ES集群的地址、用户名和密码
ES_HOST="https://10.130.245.22:9200"
ES_USER="elastic"
ES_PASS="t*mRUPeeYd8LI3CPY68-"

# 定义要添加的索引和数据
INDEX_NAME="my_index"
DATA='{"field1": "$my_index", "field2": "value2"}'

# 使用curl命令向ES集群添加索引和数据
curl -u "$ES_USER:$ES_PASS" -k -XPOST "$ES_HOST/$INDEX_NAME/_doc" -H 'Content-Type: application/json' -d "$DATA"
