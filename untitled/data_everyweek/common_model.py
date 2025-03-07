import json
import time

import requests

# 统计返回结果中某个键值对出现的次数
def count_key_value_pairs_in_json(json_str, key, value):  
    """
    :param json_str: 要解析的数据 
    :param key: 想要的key 
    :param value: 请想要的值  
    :return: 想要的键值对数据  
    """
    # 解析JSON字符串为Python对象  
    data = json.loads(json_str)  
      
    # 递归函数来统计键值对  
    def count_key_value_pairs(obj):  
        count = 0  
        if isinstance(obj, dict):  
            for k, v in obj.items():  
                if k == key and v == value:  
                    count += 1
                    print(obj['name'])  
                count += count_key_value_pairs(v)  
        elif isinstance(obj, list):  
            for item in obj:  
                count += count_key_value_pairs(item)  
        return count  
      
    # 调用递归函数并返回结果  
    return count_key_value_pairs(data) 

# 统计带有AI标识的事件
def count_event_autocheck(json_str, key):  
    """
    :param json_str: 要解析的数据 
    :param key: 想要的key 
    :return: value值不为空的数量，获取AI标识事件
    """
    # 解析JSON字符串为Python对象  
    data = json.loads(json_str)  
      
    # 递归函数来统计键值对  
    def count_key_value_pairs(obj):  
        count = 0  
        if isinstance(obj, dict):  
            for k, v in obj.items():  
                if k == key and v is not None:  
                    count += 1  
                count += count_key_value_pairs(v)  
        elif isinstance(obj, list):  
            for item in obj:  
                count += count_key_value_pairs(item)  
        return count  
      
    # 调用递归函数并返回结果  
    return count_key_value_pairs(data) 


# 统计带有AI标识的漏洞
def count_vul_autocheck(json_str, key): 
    """
    :param json_str: 要解析的数据 
    :param key: 想要的key 
    :return: value大于0的数量，获取AI标识的漏洞
    """ 
    # 解析JSON字符串为Python对象  
    data = json.loads(json_str)  
      
    # 递归函数来统计键值对  
    def count_key_value_pairs(obj):  
        count = 0  
        if isinstance(obj, dict):  
            for k, v in obj.items():  
                if k == key and v is not None and int(v) > 0: 
                    count += 1  
                count += count_key_value_pairs(v)  
        elif isinstance(obj, list):  
            for item in obj:  
                count += count_key_value_pairs(item)  
        return count  
      
    # 调用递归函数并返回结果  
    return count_key_value_pairs(data) 


#  统计返回结果某个key出现的次数
def count_key_occurrences_in_json(json_str, key):  
    """ 
    :param json_str: 要解析的数据 
    :param key: 想要的key 
    :return: 某个key出现的次数
    """
    # 解析JSON字符串为Python对象  
    data = json.loads(json_str)  
      
    # 递归函数来统计键的出现次数  
    def count_key_occurrences(obj):  
        count = 0  
        if isinstance(obj, dict):  
            # 检查键是否在字典中  
            if key in obj:  
                count += 1  
            # 递归遍历字典的值  
            for value in obj.values():  
                count += count_key_occurrences(value)  
        elif isinstance(obj, list):  
            # 递归遍历列表中的元素  
            for item in obj:  
                count += count_key_occurrences(item)  
        return count  
      
    # 调用递归函数并返回结果  
    return count_key_occurrences(data) 

# 找出相同key对应的不同的值
def find_all_keys(obj, key):
    """
    :param obj: 要处理的字典数据
    :param key: 想要的key 
    :return: 以队列返回某个key的所有值
    """  
    names = [] 
    if isinstance(obj, dict):  
        for k, v in obj.items():  
            if k == key:  
                names.append(v)  
            names.extend(find_all_keys(v, key))  
    elif isinstance(obj, list):  
        for item in obj:  
            names.extend(find_all_keys(item, key))  
    return names
 
# 获取嵌套JSON中返回的结果总数
def get_total(data):
    """
    :param data: 要处理的数据
    :return: 获取结果总数
    """ 
    if isinstance(data,dict):
        return data['data']['total'] 
    else:
        data_1 = json.loads(data)
        return data_1['data']['total'] 
# 获取工作流ID
def get_instanceid(data):
    """
    :param data: 要处理的数据
    :return: 获取工作流ID
    """ 
    if isinstance(data,dict):
        return data['data']['instanceId'] 
    else:
        data_1 = json.loads(data)
        return data_1['data']['instanceId'] 
# 获取任务复测信息
def get_retest(data,key):
    """
    :param data: 要处理的数据
    :param data: 要处理的数据
    :return: 获取复测理由
    """ 
    if isinstance(data,dict):
        return data['data'][2][key] 
    else:
        data_1 = json.loads(data)
        return data_1['data'][2][key] 
# 获取任务通过理由
def get_reson(data):
    """
    :param data: 要处理的数据
    :return: 获取结果总数
    """ 
    if isinstance(data,dict):
        return data['data'][1]['fieldValue'] 
    else:
        data_1 = json.loads(data)
        return data_1['data'][1]['fieldValue'] 




# 发送post请求无重试机制
def send_post_request(url, data, token): 

    headers = {  
    'Authorization':  f'Bearer {token}'  # 设置请求头的内容类型为JSON
    }
    # 发送POST请求  
    response = requests.post(url, headers=headers,json=data)  
      
    # 检查请求是否成功  
    if response.status_code == 200:  
        # 返回的内容可能是JSON格式，所以尝试解析  
        try:  
            # return response.json()  
            return response.text
        except json.JSONDecodeError:  
            print("返回的内容不是有效的JSON格式")  
            return response.text  
    else:  
        print(f"请求失败，状态码：{response.status_code}")  
        print(response.text)  # 打印返回的内容，便于调试  
        return None 

# 发送post请求失败并重试
def send_post_request_with_retries(url, data,author, retries=3, backoff_factor=0.3):  
    headers = {  
    'Authorization': author,  # 设置请求头的内容类型为JSON  
    # 可以添加其他自定义请求头字段  
    }
    for attempt in range(retries + 1):  
        response = requests.post(url, headers=headers,json=data)  
          
        # 检查请求是否成功  
        if response.status_code == 200:  
            # 返回的内容通常是JSON格式，所以使用json()方法解析  
            # return response.json()  
            return response.text
        else:  
            print(f"请求失败，状态码：{response.status_code}，尝试次数：{attempt + 1}")  
              
            # 如果还有重试次数，则等待一段时间后重试  
            if attempt < retries:  
                print(f"等待 {backoff_factor * (2 ** attempt)} 秒后重试...")  
                time.sleep(backoff_factor * (2 ** attempt))  # 指数退避策略  
      
    # 如果所有尝试都失败了，返回None或抛出异常  
    print("所有重试都失败了，无法获取数据")  
    return None


# 发送get请求
def send_get_request_with_author_and_params(url, token, params):  
    """  
    发送带有自定义Author请求头和参数的GET请求，并返回JSON数据。  
      
    :param url: 请求的URL  
    :param token: Author请求头的值  
    :param params: 请求参数，字典类型  
    :return: 数据，如果请求失败或响应不是JSON则返回None  
    """  
    headers = {  
        'Authorization': f'Bearer {token}'  # 自定义的Author请求头字段  
    }  
      
    response = requests.get(url, headers=headers, params=params)  
      
    # 检查请求是否成功且响应内容类型为JSON  
    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/json':  
        try:  
            return response.text
            # return response.json()  # 返回解析后的JSON数据  
        except ValueError:  
            print("Received non-JSON response.")  
            return None  
    else:  
        print(f'Request failed with status code {response.status_code}')  
        return None 